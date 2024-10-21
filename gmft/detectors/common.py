"""
Module containing methods of detecting tables from whole pdf pages.


Example:
    >>> from gmft.auto import AutoTableDetector
"""

from abc import ABC, abstractmethod

from typing import Generator, Generic, TypeVar, Union
import PIL.Image
from PIL.Image import Image as PILImage
from PIL import ImageOps # necessary to call PIL.ImageOps later

import numpy as np
from gmft.common import Rect
from gmft.pdf_bindings.common import BasePage, ImageOnlyPage
from gmft.table_captioning import _find_captions
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
    Created by :class:`.BaseDetector`.
    """
    _img: PILImage
    _img_dpi: int
    _img_padding: tuple[int, int, int, int]
    _img_margin: tuple[int, int, int, int]
    _word_height: float
    _captions: list[str]
    def __init__(self, page: BasePage, bbox: Union[tuple[int, int, int, int], Rect], confidence_score: float=1.0, label=0):
        """
        Construct a CroppedTable object.
        
        :param page: BasePage
        :param bbox: tuple of (xmin, ymin, xmax, ymax) or Rect object
        :param confidence_score: confidence score of the table detection
        :param label: label of the table detection. 
            0 means table
            1 means rotated table
        """
        
        self.page = page
        if isinstance(bbox, Rect):
            self.rect = bbox
        else:
            self.rect = Rect(bbox)
        self.confidence_score = confidence_score
        self._img = None 
        self._img_dpi = None
        self._img_padding = None
        self._img_margin = None
        self.label = label
        self._word_height = None
        self._captions = None
    
    def image(self, dpi: int = None, padding: Union[str, tuple[int, int, int, int], None]=None, margin: Union[str, tuple[int, int, int, int]]=None) -> PILImage:
        """
        Return the image of the cropped table.
        
        Following pypdfium2, scaling_factor = (dpi / 72). 
        Therefore, dpi=72 is the default, and dpi=144 is x2 zoom.
        
        :param dpi: dots per inch. If not None, the scaling_factor parameter is ignored.
        :param padding: padding (**blank pixels**) to add to the image. Tuple of (left, top, right, bottom)
            Padding (blank pixels) is added after the crop and rotation.
            Padding is important for subsequent row/column detection; see https://github.com/microsoft/table-transformer/issues/68 for discussion.
            If padding = 'auto', the padding is automatically set to 10% of the larger of {width, height}.
            Default is no padding.
        :param margin: add content (in **pdf units**) from the original pdf beyond the detected table bbox boundary.

        :return: image of the cropped table
        """
        dpi = 72 if dpi is None else dpi
        if padding == 'auto':
            width= self.rect.width * dpi / 72
            height = self.rect.height * dpi / 72
            pad = int(max(width, height) * 0.1)
            padding = (pad, pad, pad, pad)
        elif padding == None:
            padding = (0, 0, 0, 0)
        # if effective_dpi == self._img_dpi and effective_padding == self._img_padding: 
            # return self._img # cache results
        rect = self.rect
        if margin == 'auto':
            margin = (30, 30, 30, 30) # from the paper
        if margin is not None:
            
            rect = Rect((rect.xmin - margin[0], rect.ymin - margin[1], 
                         rect.xmax + margin[2], rect.ymax + margin[3]))
        img = self.page.get_image(dpi=dpi, rect=rect)
        if padding is not None:
            img = PIL.ImageOps.expand(img, padding, fill="white")
        self._img = img
        self._img_dpi = dpi
        self._img_padding = padding
        self._img_margin = margin
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
    
    def predicted_word_height(self, smallest_supported_text_height=0.1):
        """
        Get the predicted height of standard text in the table. 
        If there are no words, np.nan is returned.
        """
        if self._word_height is not None: #
            assert self._word_height != 0 # prevent infinite loop / disaster
            return self._word_height
        # get the distribution of word heights, rounded to the nearest tenth
        word_heights = []
        for xmin, ymin, xmax, ymax, text in self.text_positions(remove_table_offset=True):
            height = ymax - ymin
            if height > smallest_supported_text_height: # .1
                word_heights.append(ymax - ymin)
        
        # get the mode
        # from collections import Counter
        # word_heights = Counter(word_heights)
        
        # # set the mode to be the row height
        # # making the row less than text's height will mean that no cells are merged
        # # but subscripts may be difficult
        # row_height = 0.95 * max(word_heights, key=word_heights.get)
        
        # actually no - use the median
        if word_heights:
            self._word_height = 0.95 * float(np.median(word_heights)) # convert np.float64 to float for consistency
            assert self._word_height > 0
        else: 
            self._word_height = np.nan # empty
        return self._word_height
    
    def captions(self, margin=None, line_spacing=2.5, **kwargs) -> tuple[str, str]:
        """
        Look for a caption in the table. 
        
        Since this method is somewhat slow, the result is cached if captions() is called with default arguments.
        
        :param margin: margin around the table to search for captions. Positive margin = expands the table.
        :param line_spacing: minimum line spacing to consider two lines as separate.
        :return: tuple[str, str]: [caption_above, caption_below]
        
        """
        if self._captions and (margin is None or line_spacing == 2.5): # only cache if all default args
            return self._captions
        self._captions = _find_captions(self, margin=margin, line_spacing=line_spacing, **kwargs)
        
        return self._captions
    
    
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
        return plot_results_unwr(img, confidence=confidences, labels=labels, boxes=bboxes, id2label=None, 
                                 return_img=True, **kwargs)
    
    def to_dict(self):
        obj = {
            "filename": self.page.get_filename(),
            "page_no": self.page.page_number,
            "bbox": self.rect.bbox,
            "confidence_score": self.confidence_score,
            "label": self.label
        }
        # if self._captions:
            # obj['captions'] = self._captions
        return obj
    
    @staticmethod
    def from_dict(d: dict, page: BasePage) -> Union['CroppedTable', 'RotatedCroppedTable']:
        """
        Deserialize a CroppedTable object from dict.
        
        Because file locations may change, require the user to provide the original page - 
        but as a helper method see PyPDFium2Utils.load_page_from_dict and PyPDFium2Utils.reload
        
        These are required entries of the dict:
        - filename (str)
        - page_no (int)
        - bbox (list of x0, y0, x1, y1)
        
        These entries were formerly required:
        - confidence_score (float)
        - label (int)
        
        These entries are optional:
        - angle (one of 0, 90, 180, 270)
        
        :param d: dict
        :param page: BasePage
        :return: CroppedTable object
        """
        if 'angle' in d:
            return RotatedCroppedTable.from_dict(d, page)
        table = CroppedTable(page, d['bbox'], d.get('confidence_score', 1.0), d.get('label', 0))
        table._captions = d.get('captions', [])
        return table
    
    @staticmethod
    def from_image_only(img: PILImage) -> 'CroppedTable':
        """
        Create a :class:`.CroppedTable` object from an image only.
        
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
    
    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height


    
ConfigT = TypeVar('ConfigT')

class BaseDetector(ABC, Generic[ConfigT]):
    """
    Abstract base class for table detectors.
    """
    @abstractmethod
    def extract(self, page: BasePage, config_overrides: ConfigT=None) -> list[CroppedTable]:
        """
        Extract tables from a page.
        
        :param page: BasePage
        :param config_overrides: override the config for this call only
        :return: list of CroppedTable objects
        """
        pass
    
    def detect(self, page: BasePage, config_overrides: ConfigT=None, **kwargs) -> list[CroppedTable]:
        """
        Alias for :meth:`extract`.
        """
        return self.extract(page, config_overrides, **kwargs)


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
        
    def image(self, dpi: int = None, padding: Union[str, tuple[int, int, int, int]]=None, 
              margin: Union[str, tuple[int, int, int, int]]=None, **kwargs) -> PILImage:
        """
        Return the image of the cropped table.
        
        """
        img = super().image(dpi=dpi, padding=padding, margin=margin, **kwargs)
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
        Create a :class:`.RotatedCroppedTable` object from dict.
        """
        if 'angle' not in d:
            return CroppedTable.from_dict(d, page)
        table = RotatedCroppedTable(page, d['bbox'], d['confidence_score'], d['angle'], d['label'])
        table._captions = d.get('captions', [])
        return table
    
    # def visualize(self, **kwargs):
    #     """
    #     Visualize the cropped table.
    #     """
    #     img = self.page.get_image()
    #     plot_results_unwr(img, [self.confidence_score], [self.label], [self.bbox], self.angle, **kwargs)

    @property
    def width(self):
        if self.angle == 90 or self.angle == 270:
            return self.rect.height
        return self.rect.width

    @property
    def height(self):
        if self.angle == 90 or self.angle == 270:
            return self.rect.width
        return self.rect.height