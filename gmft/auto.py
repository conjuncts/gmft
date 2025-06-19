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

class AutoTableFormatter:
    """
    The recommended :class:`~gmft.formatters.base.BaseFormatter`. Currently points to :class:`~gmft.formatters.tatr.TATRFormatter`.
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.

    Using :meth:`extract`, a :class:`~gmft.formatters.base.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    def __new__(cls, *args, **kwargs):
        from gmft.formatters.tatr import TATRFormatter
        return TATRFormatter(*args, **kwargs)


class AutoFormatConfig:
    """
    Configuration for the recommended :class:`~gmft.formatters.base.BaseFormatter`. Currently points to :class:`~gmft.formatters.tatr.TATRFormatConfig`.
    """
    def __new__(cls, *args, **kwargs):
        from gmft.impl.tatr.config import TATRFormatConfig
        return TATRFormatConfig(*args, **kwargs)


class AutoTableDetector:
    """
    The recommended :class:`~gmft.detectors.base.BaseDetector`. Currently points to :class:`~gmft.detectors.tatr.TATRDetector`.
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.

    Using :meth:`~gmft.detectors.base.BaseDetector.extract` produces a :class:`~gmft.formatters.base.FormattedTable`, which can be exported to csv, df, etc.
    """
    def __new__(cls, *args, **kwargs):
        from gmft.detectors.tatr import TATRDetector
        return TATRDetector(*args, **kwargs)
