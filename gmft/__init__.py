"""
Currently, contains aliases for key classes and functions.

Unfortunately, although at one point the ability to import classes from the top level module (ie. `from gmft import AutoTableFormatter`) was encouraged, 
it is now discouraged and may be removed in future versions. The reason being: importing through the top level module 
loads the entire library, even when you're using only a small part of it. 

Instead, `gmft.auto` is now encouraged. For example, `from gmft.auto import AutoTableFormatter`.
"""

# See https://stackoverflow.com/q/64979364/6844235

import sys

from gmft.auto import Rect, BasePDFDocument, BasePage, CroppedTable, RotatedCroppedTable, \
    TableDetectorConfig, TableDetector, FormattedTable, TATRFormatConfig, TATRFormattedTable, \
    TATRTableDetector, TATRTableFormatter, TATRFormatConfig, \
    AutoTableFormatter, AutoFormatConfig, AutoTableDetector

# from gmft.__future__init__ import *
# not imported:
# TATRDetector
# TATRFormatter
# TATRFormatterConfig

