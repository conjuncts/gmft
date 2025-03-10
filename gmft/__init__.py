"""
Currently, contains aliases for key classes and functions.

Unfortunately, although at one point the ability to import classes from the top level module (ie. `from gmft import AutoTableFormatter`) was encouraged,
it is now discouraged and may be removed in future versions. The reason being: importing through the top level module
loads the entire library, even when you're using only a small part of it.

Instead, `gmft.auto` is now encouraged. For example, `from gmft.auto import AutoTableFormatter`.
"""

from gmft.base import Rect
from gmft.pdf_bindings.base import BasePDFDocument, BasePage
from gmft.detectors.base import CroppedTable, RotatedCroppedTable
from gmft.formatters.base import FormattedTable

from gmft.auto import (
    TATRDetector as TATRTableDetectorOrig,
    TableDetectorConfig as TableDetectorConfigOrig,
    TableDetector as TableDetectorOrig,
    TATRFormatConfig as TATRFormatConfigOrig,
    TATRFormattedTable as TATRFormattedTableOrig,
    TATRFormatter as TATRTableFormatterOrig,
    AutoTableFormatter as AutoTableFormatterOrig,
    AutoFormatConfig as AutoFormatConfigOrig,
    AutoTableDetector as AutoTableDetectorOrig,
)

has_warned = False


def _deprecation_warning(name):
    global has_warned
    if has_warned:
        return
    import warnings

    msg = f"(Deprecation) While once encouraged, \
importing {name} and other classes from the top level module is now deprecated. \
Please import from gmft.auto instead."
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    print(msg)
    has_warned = True


# These are fine, but discouraged.
# they are relatively light classes; also,
# Needed out of fear that isinstance() calls will fail
# Rect
# BasePDFDocument
# BasePage
# CroppedTable
# RotatedCroppedTable


class TATRTableDetector(TATRTableDetectorOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("TATRTableDetector")
        super().__init__(*args, **kwargs)


class TableDetectorConfig(TableDetectorConfigOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("TableDetectorConfig")
        super().__init__(*args, **kwargs)


class TableDetector(TableDetectorOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("TableDetector")
        super().__init__(*args, **kwargs)


class TATRFormatConfig(TATRFormatConfigOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("TATRFormatConfig")
        super().__init__(*args, **kwargs)


class TATRFormattedTable(TATRFormattedTableOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("TATRFormattedTable")
        super().__init__(*args, **kwargs)


class TATRTableFormatter(TATRTableFormatterOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("TATRTableFormatter")
        super().__init__(*args, **kwargs)


class AutoTableFormatter(AutoTableFormatterOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("AutoTableFormatter")
        super().__init__(*args, **kwargs)


class AutoFormatConfig(AutoFormatConfigOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("AutoFormatConfig")
        super().__init__(*args, **kwargs)


class AutoTableDetector(AutoTableDetectorOrig):
    """
    Deprecated. Please import from gmft.auto instead.
    """

    def __init__(self, *args, **kwargs):
        _deprecation_warning("AutoTableDetector")
        super().__init__(*args, **kwargs)


# Rect = LazyHouse.Rect
# BasePDFDocument = LazyHouse.BasePDFDocument
# BasePage = LazyHouse.BasePage
# CroppedTable = LazyHouse.CroppedTable
# RotatedCroppedTable = LazyHouse.RotatedCroppedTable
# TATRTableDetector = LazyHouse.TATRTableDetector
# TableDetectorConfig = LazyHouse.TableDetectorConfig
# TableDetector = LazyHouse.TableDetector
# FormattedTable = LazyHouse.FormattedTable
# TATRFormatConfig = LazyHouse.TATRFormatConfig
# TATRFormattedTable = LazyHouse.TATRFormattedTable
# TATRTableFormatter = LazyHouse.TATRTableFormatter


# AutoTableFormatter = AccessTracker(lambda x: gmft_aliases.AutoTableFormatter)
# AutoFormatConfig = AccessTracker(lambda x: gmft_aliases.AutoFormatConfig)
# AutoTableDetector = AccessTracker(lambda x: gmft_aliases.AutoTableDetector)
