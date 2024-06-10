import PIL.Image
from PIL.Image import Image as PILImage

import torch
import transformers
from transformers import AutoImageProcessor, TableTransformerForObjectDetection

from gmft.common import Rect
from gmft.pdf_bindings import BasePage, ImageOnlyPage
from gmft.table_visualization import plot_results_unwr



def position_words(words):
    
    # assume reading order is left to right, then top to bottom
    
    if not words:
        return ""
    prev_left, prev_top, prev_right, prev_bottom, lines = words[0]

    y_gap = 2 # consider the y jumping by y_gap to be a new line
    for word in words:
        x0, y0, x1, y1, text = word[:5]
        if abs(y1 - prev_bottom) >= y_gap:
            lines += f"\n{text}"
        else:
            lines += f" {text}"
        prev_bottom = y1
            
    return lines

class CroppedTable:
    _img: PILImage
    _img_dpi: int
    def __init__(self, page: BasePage, bbox: tuple[int, int, int, int] | Rect, confidence_score: float, label=0):
        
        self.page = page
        if isinstance(bbox, Rect):
            self.bbox = (int(bbox.x0), int(bbox.y0), int(bbox.x1), int(bbox.y1))
            self.rect = bbox
        else:
            self.bbox = bbox
            self.rect = Rect(bbox)
        self.confidence_score = confidence_score
        self._img = None 
        self._img_dpi = None
        self.label = label
    
    def image(self, dpi: int = None, padding: str | tuple[int, int, int, int]=None) -> PILImage:
        """
        Return the image of the cropped table.
        
        Following pypdfium2, scaling_factor = (dpi / 72). 
        Therefore, dpi=72 is the default, and dpi=144 is x2 zoom.
        
        :param dpi: dots per inch. If not None, the scaling_factor parameter is ignored.
        :param padding: padding to add to the image. Tuple of (left, top, right, bottom)
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
        if effective_dpi == self._img_dpi and effective_padding == self._img_padding: 
            return self._img # cache results
        
        img = self.page.get_image(dpi=dpi, rect=self.rect)
        if effective_padding is not None:
            img = PIL.ImageOps.expand(img, effective_padding, fill="white")
        self._img = img
        self._img_dpi = dpi
        self._img_padding = effective_padding
        return self._img
    
    def text_positions(self, remove_table_offset: bool = False):
        """
        Return the text positions of the cropped table.
        
        Any words that intersect the table are captured, even if they are not fully contained.
        
        :param remove_table_offset: if True, the positions are adjusted to be relative to the top-left corner of the table.
        :return: list of text positions, which is a tuple 
        (x0, y0, x1, y1, "string")
        """
        words = [w for w in self.page.get_positions_and_text()]
        subset = [w for w in words if Rect(w[:4]).is_intersecting(self.rect)]
        if remove_table_offset:
            subset = [(w[0] - self.rect.xmin, w[1] - self.rect.ymin, w[2] - self.rect.xmin, w[3] - self.rect.ymin, w[4]) for w in subset]
        return subset
    
    def text(self):
        """
        Return the text of the cropped table.
        
        Any words that intersect the table are captured, even if they are not fully contained.
        
        :return: text of the cropped table
        """
        return position_words(self.text_positions())
    
    def visualize(self, **kwargs):
        """
        Visualize the cropped table.
        """
        img = self.page.get_image()
        plot_results_unwr(img, [self.confidence_score], [self.label], [self.bbox], None, **kwargs)
    
    def to_dict(self):
        return {
            'filename': self.page.get_filename(),
            'page_no': self.page.page_number,
            "bbox": self.bbox,
            "confidence_score": self.confidence_score,
            "label": self.label
        }
    
    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize a CroppedTable object from dict.
        
        Because file locations have changed, require the user to provide the original page - 
        but as a helper method see pdf_bindings.load_page_from_dict
        """
        return CroppedTable(page, d['bbox'], d['confidence_score'], d['label'])
    
    @staticmethod
    def from_image_only(img: PILImage):
        """
        Create a CroppedTable object from an image only.
        
        :param img: PIL image
        """
        page = ImageOnlyPage(img)
        # bbox is the entire image
        bbox = (0, 0, img.width, img.height)
        table = CroppedTable(page, bbox, confidence_score=1.0, label=0)
        table._img = img
        table._img_dpi = 72
        return table
    


class TableDetectorConfig:
    image_processor_path: str = "microsoft/table-transformer-detection"
    detector_path: str = "microsoft/table-transformer-detection"
    warn_uninitialized_weights: bool = False

    
    def __init__(self, image_processor_path: str = None, detector_path: str = None):

        if image_processor_path is not None:
            self.image_processor_path = image_processor_path
        if detector_path is not None:
            self.detector_path = detector_path
    

class TableDetector:
    def __init__(self, config: TableDetectorConfig=None):
        if config is None:
            config = TableDetectorConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(config.image_processor_path)
        self.detector = TableTransformerForObjectDetection.from_pretrained(config.detector_path)
        
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)
    
    def extract(self, page: BasePage, threshold=0.9) -> list[CroppedTable]:
        """
        Detect tables in a page.
        
        :param page: MuPDF page
        :param threshold: how confident the model should be to consider a table
        :return: list of CroppedTable objects
        """
        img = page.get_image(72) # use standard dpi = 72, which means we don't need any scaling
        encoding = self.image_processor(img, return_tensors="pt")
        with torch.no_grad():
            outputs = self.detector(**encoding)
        # keep only predictions of queries with 0.9+ confidence (excluding no-object class)
        target_sizes = torch.tensor([img.size[::-1]])
        results = self.image_processor.post_process_object_detection(outputs, threshold=threshold, target_sizes=target_sizes)[
            0
        ]
        tables = []
        for i in range(len(results["boxes"])):
            bbox = results["boxes"][i].tolist()
            confidence_score = results["scores"][i].item()
            label = results["labels"][i].item()
            tables.append(CroppedTable(page, bbox, confidence_score, label))
        return tables
    
    

        


    
    
    
    

    