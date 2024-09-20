"""
Currently, contains aliases for key classes and functions.

Unfortunately, although at one point the ability to import classes from the top level module was encouraged, 
it is now discouraged and may be removed in future versions. 

The reason is importing through the top level module means that the whole library must be loaded 
whenever using even a small part of it. 

In lieu, `gmft.auto` is now encouraged.

See https://stackoverflow.com/q/64979364/6844235
"""

import sys
# from gmft.auto import *

from gmft.auto import Rect, BasePDFDocument, BasePage, CroppedTable, RotatedCroppedTable, \
    TableDetectorConfig, TableDetector, FormattedTable, TATRFormatterConfig, TATRFormattedTable, \
    TATRTableDetector, TATRTableFormatter, TATRFormatConfig, \
    AutoTableFormatter, AutoFormatConfig, AutoTableDetector

# not imported:
# TATRDetector
# TATRFormatter
# TATRFormatterConfig

