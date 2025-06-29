"""
Currently, contains aliases for key classes and functions.

Importing from the top-level module previously resulted in long load times.
However, v0.5 introduces lazy loading, which greatly improves the situation.

Now, classes may either be imported from their original locations,
`gmft.auto`, or from here, where they will be lazy loaded.
"""

# small classes are fine, but discouraged.
from gmft.base import Rect
from gmft.core.legacy.mirror import DeprecationMirrorMeta
from gmft.pdf_bindings.base import BasePDFDocument, BasePage
from gmft.detectors.base import CroppedTable, RotatedCroppedTable
from gmft.formatters.base import FormattedTable

# config-only classes specific to TATR are still discouraged.

# these auto classes are lazy-loaded
from gmft.core.auto_lazy import (
    AutoTableFormatter,
    AutoFormatConfig,
    AutoTableDetector,
)

# We need to support these imports for compatibility:
# TATRTableDetector
# TableDetectorConfig
# TableDetector
# TATRFormatConfig
# TATRFormattedTable
# TATRTableFormatter
# AutoTableFormatter
# AutoFormatConfig
# AutoTableDetector


# These bulky TATR-specific detectors are discouraged, but still available for compatibility.
class TATRTableDetector(metaclass=DeprecationMirrorMeta):
    """
    This import is deprecated.

    Please use:
    - gmft.AutoTableDetector
    - gmft.detectors.tatr.TATRDetector
    """

    @classmethod
    def get_mirrored_class(cls):
        from gmft.detectors.tatr import TATRDetector as OrigCls

        return OrigCls


class TableDetectorConfig(metaclass=DeprecationMirrorMeta):
    """
    This import is deprecated.

    Please use:
    - Reformat API (v0.5)
    - gmft.detectors.tatr.TATRDetectorConfig
    """

    @classmethod
    def get_mirrored_class(cls):
        from gmft.impl.tatr.config import TATRDetectorConfig as OrigCls

        return OrigCls


class TableDetector(metaclass=DeprecationMirrorMeta):
    """
    This import is deprecated.

    Please use:
    - gmft.AutoTableDetector
    - gmft.detectors.tatr.TATRDetector
    """

    @classmethod
    def get_mirrored_class(cls):
        from gmft.auto import TATRDetector as OrigCls

        return OrigCls


class TATRFormatConfig(metaclass=DeprecationMirrorMeta):
    """
    This import is deprecated.

    Please use:
    - Reformat API (v0.5)
    - gmft.formatters.tatr.TATRFormatConfig
    """

    @classmethod
    def get_mirrored_class(cls):
        from gmft.impl.tatr.config import TATRFormatConfig as OrigCls

        return OrigCls


class TATRFormattedTable(metaclass=DeprecationMirrorMeta):
    """
    This import is deprecated.

    Please use:
    - Reformat API (v0.5)
    - gmft.formatters.tatr.TATRFormattedTable
    """

    @classmethod
    def get_mirrored_class(cls):
        from gmft.formatters.tatr import TATRFormattedTable as OrigCls

        return OrigCls


class TATRTableFormatter(metaclass=DeprecationMirrorMeta):
    """
    This import is deprecated.

    Please use:
    - gmft.auto.AutoTableFormatter
    - gmft.formatters.tatr.TATRFormatter
    """

    @classmethod
    def get_mirrored_class(cls):
        from gmft.formatters.tatr import TATRFormatter as OrigCls

        return OrigCls
