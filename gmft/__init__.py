"""
Contains aliases for key classes and functions.

It is recommended to import classes using **this** top-level file. Exact paths may change in future versions.
"""


from gmft.table_detection import CroppedTable, RotatedCroppedTable, TATRTableDetector, TableDetector, TableDetectorConfig
from gmft.common import Rect
from gmft.table_function import TATRFormatConfig, TATRFormattedTable, TATRTableFormatter, FormattedTable
from gmft.pdf_bindings import BasePDFDocument, BasePage

class AutoTableFormatter(TATRTableFormatter):
    """
    The recommended :class:`~gmft.table_function.TableFormatter`. Currently points to :class:`~gmft.table_function.TATRTableFormatter`.
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`~gmft.table_function.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    pass

class AutoFormatConfig(TATRFormatConfig):
    """
    Configuration for the recommended :class:`~gmft.table_function.TableFormatter`. Currently points to :class:`~gmft.table_function.TATRFormatConfig`.
    """
    pass

class AutoTableDetector(TATRTableDetector):
    """
    The recommended :class:`~gmft.table_detection.TableDetector`. Currently points to :class:`~gmft.table_detection.TATRTableDetector`.
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract` produces a :class:`~gmft.table_function.FormattedTable`, which can be exported to csv, df, etc.
    """
    pass
