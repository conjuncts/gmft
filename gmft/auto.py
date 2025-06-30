"""
Contains aliases for key classes and functions.

For convenience, please import using `gmft.auto` instead of `gmft`.
"""

from gmft.base import Rect
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.pdf_bindings.base import BasePDFDocument, BasePage
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.detectors.base import CroppedTable, RotatedCroppedTable
from gmft.detectors.tatr import (
    TATRDetector,
    TATRDetectorConfig,
    TableDetectorConfig,
    TableDetector,
)
from gmft.formatters.base import FormattedTable
from gmft.formatters.tatr import TATRFormattedTable, TATRFormatter

TATRTableDetector = TATRDetector
TATRTableFormatter = TATRFormatter
# TATRFormatConfig = TATRFormatConfig

from gmft.core.auto_lazy import (
    AutoTableFormatter,
    AutoFormatConfig,
    AutoTableDetector,
)
