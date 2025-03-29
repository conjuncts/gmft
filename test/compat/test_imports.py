# ruff: noqa


def test_aliases():
    """
    make sure that the now deprecated ability to import from top level module
    isn't completely broken

    """
    from gmft import Rect

    from gmft import (
        TATRFormattedTable,
        AutoFormatConfig,
        AutoTableFormatter,
        CroppedTable,
        AutoFormatConfig,
        AutoTableDetector,
        AutoTableFormatter,
    )

    obj = Rect((1, 2, 3, 4))
    assert obj.xmin == 1
    assert obj.ymin == 2

    # make sure that these work
    from gmft import (
        Rect,
        BasePDFDocument,
        BasePage,
        CroppedTable,
        RotatedCroppedTable,
        TableDetectorConfig,
        TableDetector,
        FormattedTable,
        TATRFormatConfig,
        TATRFormattedTable,
        TATRTableDetector,
        TATRTableFormatter,
        TATRFormatConfig,
        AutoTableFormatter,
        AutoFormatConfig,
        AutoTableDetector,
    )

    ct = CroppedTable(None, (1, 2, 3, 4), 0.9)
    assert ct.confidence_score == 0.9
    assert isinstance(ct, CroppedTable)

    from gmft.detectors.base import CroppedTable as CroppedTableOrig

    assert isinstance(ct, CroppedTableOrig)

    from gmft import TATRFormatConfig

    config = TATRFormatConfig(large_table_threshold=2)
    assert config.large_table_threshold == 2

    assert isinstance(config, TATRFormatConfig)

    # import from "common" as an alias for "base"
    from gmft.common import Rect as CommonRect
    from gmft.formatters.common import BaseFormatter

    common_rect = CommonRect((1, 2, 3, 4))
    rect = Rect((1, 2, 3, 4))
    assert isinstance(common_rect, Rect)
    assert isinstance(common_rect, CommonRect)
    assert isinstance(rect, Rect)
    assert isinstance(rect, CommonRect)

    # import from table_detection and table_function
    from gmft.table_detection import CroppedTable as CroppedTableAliased
    from gmft.table_function import TATRFormatter
