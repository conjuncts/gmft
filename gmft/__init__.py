"""
Contains aliases for key classes and functions.

It is recommended to import classes using **this** top-level file. Exact paths may change in future versions.
"""


from gmft.table_detection import CroppedTable, TableDetector, TableDetectorConfig
from gmft.common import Rect
from gmft.table_function import TATRFormatConfig, TATRFormattedTable, TATRTableFormatter, AutoTableFormatter, AutoFormatConfig, FormattedTable
from gmft.pdf_bindings import BasePDFDocument, BasePage

