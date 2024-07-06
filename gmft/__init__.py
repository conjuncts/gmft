"""
Contains aliases for key classes and functions.

It is recommended to import classes using **this** top-level file. Exact paths may change in future versions.
"""


from gmft.table_detection import CroppedTable, TATRTableDetector, TableDetector, TableDetectorConfig
from gmft.common import Rect
from gmft.table_function import TATRFormatConfig, TATRFormattedTable, TATRTableFormatter, FormattedTable
from gmft.pdf_bindings import BasePDFDocument, BasePage

class AutoTableFormatter(TATRTableFormatter):
    """
    The recommended :class:`TableFormatter`. Currently points to :class:`~gmft.TATRTableFormatter`.
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`~gmft.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    pass

class AutoFormatConfig(TATRFormatConfig):
    """
    Configuration for the recommended :class:`TableFormatter`. Currently points to :class:`~gmft.TATRFormatConfig`.
    """
    pass

class AutoTableDetector(TATRTableDetector):
    """
    The recommended :class:`~gmft.TableDetector`. Currently points to :class:`~gmft.TATRTableDetector`.
    Uses TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract` produces a :class:`~gmft.FormattedTable`, which can be exported to csv, df, etc.
    """
    pass
