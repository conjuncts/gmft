# make sure that imports aren't completely broken

def test_aliases():
    from gmft import Rect

    from gmft import TATRFormattedTable, AutoFormatConfig, AutoTableFormatter, CroppedTable, AutoFormatConfig, AutoTableDetector, AutoTableFormatter
    obj = Rect((1, 2, 3, 4))
    assert obj.xmin == 1
    assert obj.ymin == 2

    from gmft.table_detection import CroppedTable
    