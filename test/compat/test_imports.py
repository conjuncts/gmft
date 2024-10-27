# 

def test_aliases():
    """
    make sure that the now deprecated ability to import from top level module
    isn't completely broken

    """
    from gmft import Rect

    from gmft import TATRFormattedTable, AutoFormatConfig, AutoTableFormatter, CroppedTable, AutoFormatConfig, AutoTableDetector, AutoTableFormatter
    obj = Rect((1, 2, 3, 4))
    assert obj.xmin == 1
    assert obj.ymin == 2



    from gmft.table_detection import CroppedTable as CroppedTableAliased

    # make sure that these work
    from gmft import Rect, BasePDFDocument, BasePage, CroppedTable, RotatedCroppedTable, \
    TableDetectorConfig, TableDetector, FormattedTable, TATRFormatConfig, TATRFormattedTable, \
    TATRTableDetector, TATRTableFormatter, TATRFormatConfig, \
    AutoTableFormatter, AutoFormatConfig, AutoTableDetector

    ct = CroppedTable(None, (1, 2, 3, 4), 0.9)
    assert ct.confidence_score == 0.9
    assert isinstance(ct, CroppedTable)

    from gmft.detectors.common import CroppedTable as CroppedTableOrig
    assert isinstance(ct, CroppedTableOrig)

    from gmft import TATRFormatConfig
    config = TATRFormatConfig(large_table_threshold=2)
    assert config.large_table_threshold == 2

    assert isinstance(config, TATRFormatConfig)


    