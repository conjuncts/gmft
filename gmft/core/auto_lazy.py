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
