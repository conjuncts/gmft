"""
Module containing methods of detecting tables from whole pdf pages.

Whenever possible, classes (like :class:`TableDetector`) should be imported from the top-level module, not from this module,
as the exact paths may change in future versions.

Example:
    >>> from gmft import TableDetector
"""

from typing import Generator, Union
import PIL.Image
from PIL.Image import Image as PILImage

import torch
import transformers
from transformers import AutoImageProcessor, TableTransformerForObjectDetection

from gmft.common import Rect
from gmft.pdf_bindings.common import BasePage, ImageOnlyPage
from gmft.table_visualization import plot_results_unwr



def position_words(words: Generator[tuple[int, int, int, int, str], None, None], y_gap=3):
    """
    Helper function to convert a list of words with positions to a string.
    """
    
    # assume reading order is left to right, then top to bottom
    
    first = next(words, None)
    
    if first is None:
        return ""
    
    prev_left, prev_top, prev_right, prev_bottom, lines = first

    # y_gap = 2 # consider the y jumping by y_gap to be a new line
    for word in words:
        x0, y0, x1, y1, text = word[:5]
        if abs(y1 - prev_bottom) >= y_gap:
            lines += f"\n{text}"
        else:
            lines += f" {text}"
        prev_bottom = y1
            
    return lines

class CroppedTable:
    """
    A pdf selection, cropped to include just a table. 
    Created by :class:`~gmft.TableDetector`.
    """
    _img: PILImage
    _img_dpi: int
    _img_padding: tuple[int, int, int, int]
    def __init__(self, page: BasePage, bbox: tuple[int, int, int, int] | Rect, confidence_score: float, label=0):
        
        self.page = page
        if isinstance(bbox, Rect):
            self.rect = bbox
        else:
            self.rect = Rect(bbox)
        self.confidence_score = confidence_score
        self._img = None 
        self._img_dpi = None
        self._img_padding = None
        self.label = label
    
    def image(self, dpi: int = None, padding: str | tuple[int, int, int, int]=None) -> PILImage:
        """
        Return the image of the cropped table.
        
        Following pypdfium2, scaling_factor = (dpi / 72). 
        Therefore, dpi=72 is the default, and dpi=144 is x2 zoom.
        
        :param dpi: dots per inch. If not None, the scaling_factor parameter is ignored.
        :param padding: padding to add to the image. Tuple of (left, top, right, bottom)
            Padding is added after the crop and rotation.
            Padding is important for subsequent row/column detection; see https://github.com/microsoft/table-transformer/issues/68 for discussion.
            If padding = 'auto', the padding is automatically set to 10% of the larger of {width, height}.
        :return: image of the cropped table
        """
        effective_dpi = 72 if dpi is None else dpi
        effective_padding = padding
        if padding == 'auto':
            width= self.rect.width * effective_dpi / 72
            height = self.rect.height * effective_dpi / 72
            pad = int(max(width, height) * 0.1)
            effective_padding = (pad, pad, pad, pad)
        # if effective_dpi == self._img_dpi and effective_padding == self._img_padding: 
            # return self._img # cache results
        
        img = self.page.get_image(dpi=dpi, rect=self.rect)
        if effective_padding is not None:
            img = PIL.ImageOps.expand(img, effective_padding, fill="white")
        self._img = img
        self._img_dpi = effective_dpi
        self._img_padding = effective_padding
        return self._img
    
    def text_positions(self, remove_table_offset: bool = False, outside: bool = False) -> Generator[tuple[int, int, int, int, str], None, None]:
        """
        Return the text positions of the cropped table.
        
        Any words that intersect the table are captured, even if they are not fully contained.
        
        :param remove_table_offset: if True, the positions are adjusted to be relative to the top-left corner of the table.
        :param outside: if True, returns the **complement** of the table: all the text positions outside the table.
            By default, it returns the text positions inside the table.
        :return: list of text positions, which is a tuple 
            ``(x0, y0, x1, y1, "string")``
        """
        for w in self.page.get_positions_and_text():
            if Rect(w[:4]).is_intersecting(self.rect) != outside:
                if remove_table_offset:
                    yield (w[0] - self.rect.xmin, w[1] - self.rect.ymin, w[2] - self.rect.xmin, w[3] - self.rect.ymin, w[4])
                else:
                    yield w
        # words = [w for w in self.page.get_positions_and_text()]
        # if outside:
        #     # get the table's complement
        #     subset = [w for w in words if not Rect(w[:4]).is_intersecting(self.rect)]
        # else:
        #     # get the table
        #     subset = [w for w in words if Rect(w[:4]).is_intersecting(self.rect)]
        # if remove_table_offset:
        #     subset = [(w[0] - self.rect.xmin, w[1] - self.rect.ymin, w[2] - self.rect.xmin, w[3] - self.rect.ymin, w[4]) for w in subset]
        # return subset
    
    def text(self):
        """
        Return the text of the cropped table.
        
        Any words that intersect the table are captured, even if they are not fully contained.
        
        :return: text of the cropped table
        """
        return position_words(self.text_positions())
    
    def visualize(self, show_text=False, **kwargs):
        """
        Visualize the cropped table.
        """
        img = self.page.get_image()
        confidences = [self.confidence_score]
        labels = [self.label]
        bboxes = [self.rect.bbox]
        if show_text:
            # text_positions = [(x0, y0, x1, y1) for x0, y0, x1, y1, _ in self.text_positions()]
            text_positions = [w[:4] for w in self.page.get_positions_and_text()]
            confidences += [0.9] * len(text_positions)
            labels += [-1] * len(text_positions)
            bboxes += text_positions
        plot_results_unwr(img, confidence=confidences, labels=labels, boxes=bboxes, id2label=None, **kwargs)
    
    def to_dict(self):
        return {
            "filename": self.page.get_filename(),
            "page_no": self.page.page_number,
            "bbox": self.rect.bbox,
            "confidence_score": self.confidence_score,
            "label": self.label
        }
    
    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize a CroppedTable object from dict.
        
        Because file locations may change, require the user to provide the original page - 
        but as a helper method see PyPDFium2Utils.load_page_from_dict and PyPDFium2Utils.reload
        
        :param d: dict
        :param page: BasePage
        :return: CroppedTable object
        """
        if 'angle' in d:
            return RotatedCroppedTable.from_dict(d, page)
        return CroppedTable(page, d['bbox'], d['confidence_score'], d['label'])
    
    @staticmethod
    def from_image_only(img: PILImage) -> 'CroppedTable':
        """
        Create a :class:`~gmft.CroppedTable` object from an image only.
        
        :param img: PIL image
        :return: CroppedTable object
        """
        page = ImageOnlyPage(img)
        # bbox is the entire image
        bbox = (0, 0, img.width, img.height)
        table = CroppedTable(page, bbox, confidence_score=1.0, label=0)
        table._img = img
        table._img_dpi = 72
        return table
    
    @property
    def bbox(self):
        return self.rect.bbox


class TableDetectorConfig:
    """
    Configuration for the :class:`~gmft.TableDetector` class.
    """
    image_processor_path: str = "microsoft/table-transformer-detection"
    detector_path: str = "microsoft/table-transformer-detection"
    warn_uninitialized_weights: bool = False
    
    # How confident the model should be to consider a table
    detector_base_threshold: float = 0.9

    
    def __init__(self, image_processor_path: str = None, detector_path: str = None):

        if image_processor_path is not None:
            self.image_processor_path = image_processor_path
        if detector_path is not None:
            self.detector_path = detector_path
    

class TableDetector:
    """
    Detects tables in a pdf page. Default implementation uses TableTransformerForObjectDetection.
    """
    def __init__(self, config: TableDetectorConfig=None, default_implementation=True):
        """
        Initialize the TableDetector.
        
        :param config: TableDetectorConfig
        :param default_implementation: Should be True, unless you are writing a custom subclass for TableDetector.
        """
        
        # future-proofing: allow subclasses for TableDetector to have different architectures
        if not default_implementation:
            return
        
        if config is None:
            config = TableDetectorConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(config.image_processor_path)
        self.detector = TableTransformerForObjectDetection.from_pretrained(config.detector_path)
        
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)
        self.config = config
    
    def extract(self, page: BasePage) -> list[CroppedTable]:
        """
        Detect tables in a page.
        
        :param page: BasePage
        :return: list of CroppedTable objects
        """
        img = page.get_image(72) # use standard dpi = 72, which means we don't need any scaling
        encoding = self.image_processor(img, return_tensors="pt")
        with torch.no_grad():
            outputs = self.detector(**encoding)
        # keep only predictions of queries with 0.9+ confidence (excluding no-object class)
        target_sizes = torch.tensor([img.size[::-1]])
        threshold = self.config.detector_base_threshold
        results = self.image_processor.post_process_object_detection(outputs, threshold=threshold, target_sizes=target_sizes)[
            0
        ]
        tables = []
        for i in range(len(results["boxes"])):
            bbox = results["boxes"][i].tolist()
            confidence_score = results["scores"][i].item()
            label = results["labels"][i].item()
            if label == 1:
                tables.append(RotatedCroppedTable(page, bbox, confidence_score, 90, label))
            else:
                tables.append(CroppedTable(page, bbox, confidence_score, label))
        return tables

class TATRTableDetector(TableDetector):
    """
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract` produces a :class:`~gmft.FormattedTable`, which can be exported to csv, df, etc.
    """
    pass

class AutoTableDetector(TATRTableDetector):
    """
    The recommended :class:`~gmft.TableDetector`. Currently points to :class:`~gmft.TATRTableDetector`.
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract` produces a :class:`~gmft.FormattedTable`, which can be exported to csv, df, etc.
    """
    pass

class RotatedCroppedTable(CroppedTable):
    """
    Table that has been rotated. 
    
    Note: ``self.bbox`` and ``self.rect`` are in coordinates of the original pdf.
    But text_positions() can possibly give transformed coordinates.
    
    Currently, only 0, 90, 180, and 270 degree rotations are supported.
    An angle of 90 would mean that a 90 degree cc rotation has been applied to a level image. 
    
    In practice, the majority of rotated tables are rotated by 90 degrees.
    """
    
    def __init__(self, page: BasePage, bbox: tuple[int, int, int, int], confidence_score: float, angle: float, label=0):
        """
        Currently, only 0, 90, 180, and 270 degree rotations are supported.
        
        :param page: BasePage
        :param angle: angle in degrees, counterclockwise. 
            That is, 90 would mean that a 90 degree cc rotation has been applied to a level image. 
            In practice, the majority of rotated tables are rotated by 90 degrees.
        
        """
        super().__init__(page, bbox, confidence_score, label)
        
        if angle not in [0, 90, 180, 270]:
            raise ValueError("Only 0, 90, 180, 270 are supported.")
        self.angle = angle
        
    def image(self, dpi: int = None, padding: str | tuple[int, int, int, int]=None) -> PILImage:
        """
        Return the image of the cropped table.
        
        """
        img = super().image(dpi=dpi, padding=padding)
        # if self.angle == 90:
        if self.angle != 0:
            # rotate by negative angle to get back to original orientation
            img = img.rotate(-self.angle, expand=True)
            
        return img
    
    def text_positions(self, remove_table_offset: bool = False, outside: bool = False) -> Generator[tuple[int, int, int, int, str], None, None]:
        """
        Return the text positions of the cropped table.
        
        If remove_table_offset is False, positions are relative to the top-left corner of the pdf (no adjustment for rotation).
        
        If remove_table_offset is True, positions are relative to a hypothetical pdf where the text in the table is perfectly level, and 
        pdf's top-left corner is also the table's top-left corner (both at 0, 0).
        
        :param remove_table_offset: if True, the positions are adjusted to be relative to the top-left corner of the table. 
        :param outside: if True, returns the **complement** of the table: all the text positions outside the table.
        :return: list of text positions, which are tuples of (xmin, ymin, xmax, ymax, "string")
        """
        if self.angle == 0 or remove_table_offset == False:
            yield from super().text_positions(remove_table_offset=remove_table_offset, outside=outside)
        elif self.angle == 90:
            for w in super().text_positions(remove_table_offset=True, outside=outside):
                x0, y0, x1, y1, text = w
                x0, y0, x1, y1 = self.rect.height - y1, x0, self.rect.height - y0, x1
                yield (x0, y0, x1, y1, text)
        elif self.angle == 180:
            for w in super().text_positions(remove_table_offset=True, outside=outside):
                x0, y0, x1, y1, text = w
                x0, y0, x1, y1 = self.rect.width - x1, self.rect.height - y1, self.rect.width - x0, self.rect.height - y0
                yield (x0, y0, x1, y1, text)
        elif self.angle == 270:
            for w in super().text_positions(remove_table_offset=True, outside=outside):
                x0, y0, x1, y1, text = w
                x0, y0, x1, y1 = y0, self.rect.width - x1, y1, self.rect.width - x0
                yield (x0, y0, x1, y1, text)
    
    def to_dict(self):
        d = super().to_dict()
        d['angle'] = self.angle
        return d
    
    @staticmethod
    def from_dict(d: dict, page: BasePage) -> Union[CroppedTable, 'RotatedCroppedTable']:
        """
        Create a :class:`CroppedRotatedTable` object from dict.
        """
        if 'angle' not in d:
            return CroppedTable.from_dict(d, page)
        return RotatedCroppedTable(page, d['bbox'], d['confidence_score'], d['angle'], d['label'])
    
    # def visualize(self, **kwargs):
    #     """
    #     Visualize the cropped table.
    #     """
    #     img = self.page.get_image()
    #     plot_results_unwr(img, [self.confidence_score], [self.label], [self.bbox], self.angle, **kwargs)
    
    

        


    
    
    
    

    