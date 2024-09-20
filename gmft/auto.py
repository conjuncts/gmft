"""
Contains aliases for key classes and functions.

For convenience, please import using `gmft.auto` instead of `gmft`. 
"""

from gmft.common import Rect
from gmft.pdf_bindings import BasePDFDocument, BasePage
from gmft.detectors.common import CroppedTable, RotatedCroppedTable
from gmft.detectors.tatr import TATRDetector, TableDetectorConfig, TableDetector
from gmft.formatters.common import FormattedTable
from gmft.formatters.tatr import TATRFormatterConfig, TATRFormattedTable, TATRFormatter

TATRTableDetector = TATRDetector
TATRTableFormatter = TATRFormatter
TATRFormatConfig = TATRFormatterConfig


class AutoTableFormatter(TATRFormatter):
    """
    The recommended :class:`~gmft.formatters.common.BaseFormatter`. Currently points to :class:`~gmft.formatters.tatr.TATRFormatter`.
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`~gmft.formatters.common.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    pass

class AutoFormatConfig(TATRFormatterConfig):
    """
    Configuration for the recommended :class:`~gmft.formatters.common.BaseFormatter`. Currently points to :class:`~gmft.formatters.tatr.TATRFormatterConfig`.
    """
    pass

class AutoTableDetector(TATRDetector):
    """
    The recommended :class:`~gmft.detectors.common.BaseDetector`. Currently points to :class:`~gmft.detectors.tatr.TATRDetector`.
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`~gmft.detectors.common.BaseDetector.extract` produces a :class:`~gmft.formatters.common.FormattedTable`, which can be exported to csv, df, etc.
    """
    pass
