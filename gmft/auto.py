"""
Original content of __init__.py, this contains aliases for key classes and functions.

For convenience, you can still always import classes using `gmft.auto`. Exact paths may change in future versions.
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
    The recommended :class:`~gmft.table_function.TableFormatter`. Currently points to :class:`~gmft.table_function.TATRTableFormatter`.
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`~gmft.table_function.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    pass

class AutoFormatConfig(TATRFormatterConfig):
    """
    Configuration for the recommended :class:`~gmft.table_function.TableFormatter`. Currently points to :class:`~gmft.table_function.TATRFormatConfig`.
    """
    pass

class AutoTableDetector(TATRDetector):
    """
    The recommended :class:`~gmft.table_detection.TableDetector`. Currently points to :class:`~gmft.table_detection.TATRTableDetector`.
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract` produces a :class:`~gmft.table_function.FormattedTable`, which can be exported to csv, df, etc.
    """
    pass
