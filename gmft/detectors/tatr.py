import copy
from dataclasses import dataclass
import torch
from gmft.core._dataclasses import with_config
from gmft.core.ml import _resolve_device
from gmft.detectors.base import BaseDetector, CroppedTable, RotatedCroppedTable
from gmft.base import Rect

from gmft.impl.tatr.config import TATRDetectorConfig
from gmft.pdf_bindings.base import BasePage


class TATRDetector(BaseDetector[TATRDetectorConfig]):
    """
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.

    Using :meth:`extract` produces a :class:`.FormattedTable`, which can be exported to csv, df, etc.

    Detects tables in a pdf page. Default implementation uses TableTransformerForObjectDetection.
    """

    def __init__(self, config: TATRDetectorConfig = None, default_implementation=True):
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
        self.image_processor = AutoImageProcessor.from_pretrained(
            config.image_processor_path
        )

        revision = "no_timm" if config.no_timm else None
        self.detector = TableTransformerForObjectDetection.from_pretrained(
            config.detector_path, revision=revision
        ).to(_resolve_device(config.torch_device))

        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)
        self.config = config

    def extract(
        self, page: BasePage, config_overrides: TATRDetectorConfig = None, rect: Rect = None
    ) -> list[CroppedTable]:
        """
        Detect tables in a page.

        :param page: BasePage
        :param config_overrides: Optional config overrides for this extraction
        :param rect: Optional Rect to constrain detection within given dimensions
        :return: list of CroppedTable objects
        """
        config = with_config(self.config, config_overrides)

        img = page.get_image(
            72, rect=rect
        )  # use standard dpi = 72, which means we don't need any scaling
        encoding = self.image_processor(img, return_tensors="pt").to(
            _resolve_device(self.config.torch_device)
        )
        with torch.no_grad():
            outputs = self.detector(**encoding)
        # keep only predictions of queries with 0.9+ confidence (excluding no-object class)
        target_sizes = torch.tensor([img.size[::-1]])
        threshold = config.detector_base_threshold
        results = self.image_processor.post_process_object_detection(
            outputs, threshold=threshold, target_sizes=target_sizes
        )[0]
        tables = []
        for i in range(len(results["boxes"])):
            bbox = results["boxes"][i].tolist()
            confidence_score = results["scores"][i].item()
            label = results["labels"][i].item()
            if label == 1:
                tables.append(
                    RotatedCroppedTable(page, bbox, confidence_score, 90, label)
                )
            else:
                tables.append(CroppedTable(page, bbox, confidence_score, label))
        return tables


# legacy aliases from the nonstandard days
TableDetector = TATRDetector
TableDetectorConfig = TATRDetectorConfig

TATRTableDetector = TATRDetector
TATRTableDetectorConfig = TATRDetectorConfig
