from gmft.formatters.tatr import TATRFormattedTable
from gmft.impl.tatr.config import TATRFormatConfig


header_top_gap = {
    "filename": "data/pdfs/tiny.pdf",
    "page_no": 0,
    "bbox": [
        76.66205596923828,
        162.82687377929688,  # y-top = 162
        440.9659729003906,
        248.67056274414062,
    ],
    "confidence_score": 0.9996763467788696,
    "label": 0,
    "fctn_scale_factor": 2.0,
    "fctn_padding": [72, 72, 72, 72],
    "config": {},
    "outliers": {},
    "fctn_results": {
        "scores": [
            0.9999,
            0.9998,
            0.9999,
            # 0.9998,
            0.9999,
            0.9998,
            0.9998,
            0.9897,
            0.9998,
        ],
        "labels": [
            2,
            2,
            1,  # 2,
            1,
            1,
            2,
            3,
            0,
        ],
        "boxes": [
            [71.36, 159.07, 797.01, 206.53],
            [70.94, 110.53, 797.12, 158.92],
            [71.17, 75.58, 329.65, 244.52],
            # [71.13, 75.61, 797.35, 109.99],  # the row coincident with header
            [331.35, 75.64, 576.94, 244.35],
            [575.64, 75.62, 797.51, 244.22],
            [71.27, 206.54, 796.82, 244.68],
            [71.13, 75.61, 797.36, 109.93],  # the true header row
            [71.12, 75.54, 797.08, 244.42],
        ],
    },
}


def test_should_print_top_gap(doc_tiny, caplog):
    # Should print "gmft - INFO - Filling in gap at top of table"
    # Run with: pytest -s test/formatters/tatr/test_top.py::test_should_print_top_gap

    ft = TATRFormattedTable.from_dict(header_top_gap, doc_tiny[0])

    # something should be logged
    with caplog.at_level("INFO"):
        ft.df(config_overrides=TATRFormatConfig(verbosity=2))

    assert "Filling in gap at top of table" in caplog.text

    caplog.clear()

    # something should not be logged
    with caplog.at_level("INFO"):
        ft.df(config_overrides=TATRFormatConfig(verbosity=1))

    assert "Filling in gap at top of table" not in caplog.text
