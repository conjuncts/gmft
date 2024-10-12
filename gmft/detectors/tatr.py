import copy
from dataclasses import dataclass
import torch
from gmft._dataclasses import with_config
from gmft.detectors.common import BaseDetector, CroppedTable, RotatedCroppedTable

from gmft.pdf_bindings.common import BasePage


@dataclass
class TATRDetectorConfig:
    """
    Configuration for the :class:`.TATRDetector` class.
    
    Specific to the TableTransformerForObjectDetection model. (Do not subclass this.)
    """
    image_processor_path: str = "microsoft/table-transformer-detection"
    detector_path: str = "microsoft/table-transformer-detection"
    no_timm: bool = True # huggingface revision
    warn_uninitialized_weights: bool = False
    torch_device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    detector_base_threshold: float = 0.9
    """Minimum confidence score required for a table"""

    @property
    def confidence_score_threshold(self):
        raise DeprecationWarning("Use detector_base_threshold instead.")
    @confidence_score_threshold.setter
    def confidence_score_threshold(self, value):
        raise DeprecationWarning("Use detector_base_threshold instead.")
    
    # def __init__(self, image_processor_path: str = None, detector_path: str = None, torch_device: str = None):

    #     if image_processor_path is not None:
    #         self.image_processor_path = image_processor_path
    #     if detector_path is not None:
    #         self.detector_path = detector_path
    #     if torch_device is not None:
    #         self.torch_device = torch_device
    
    def __post_init__(self):
        # use cuda if available
        pass



class TATRDetector(BaseDetector[TATRDetectorConfig]):
    """
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract` produces a :class:`.FormattedTable`, which can be exported to csv, df, etc.

    Detects tables in a pdf page. Default implementation uses TableTransformerForObjectDetection.
    """
    def __init__(self, config: TATRDetectorConfig=None, default_implementation=True):
        """
        Initialize the TableDetector.
        
        :param config: TATRDetectorConfig
        :param default_implementation: Should be True, unless you are writing a custom subclass for TableDetector.
        """
        
        import transformers
        from transformers import AutoImageProcessor, TableTransformerForObjectDetection

        
        # future-proofing: allow subclasses for TableDetector to have different architectures
        if not default_implementation:
            return
        
        if config is None:
            config = TATRDetectorConfig()
        elif isinstance(config, dict):
            config = TATRDetectorConfig(**config)
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(config.image_processor_path)
        
        revision = "no_timm" if config.no_timm else None
        self.detector = TableTransformerForObjectDetection.from_pretrained(config.detector_path, revision=revision).to(config.torch_device)
        
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)
        self.config = config
    
    def extract(self, page: BasePage, config_overrides: TATRDetectorConfig=None) -> list[CroppedTable]:
        """
        Detect tables in a page.
        
        :param page: BasePage
        :param config_overrides: override the config for this call only
        :return: list of CroppedTable objects
        """
        config = with_config(self.config, config_overrides)
        
        img = page.get_image(72) # use standard dpi = 72, which means we don't need any scaling
        encoding = self.image_processor(img, return_tensors="pt").to(self.config.torch_device)
        with torch.no_grad():
            outputs = self.detector(**encoding)
        # keep only predictions of queries with 0.9+ confidence (excluding no-object class)
        target_sizes = torch.tensor([img.size[::-1]])
        threshold = config.detector_base_threshold
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
    

# legacy aliases from the nonstandard days
TableDetector = TATRDetector
TableDetectorConfig = TATRDetectorConfig

TATRTableDetector = TATRDetector
TATRTableDetectorConfig = TATRDetectorConfig
