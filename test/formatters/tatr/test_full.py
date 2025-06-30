import json
import pandas as pd
from pandas.testing import assert_frame_equal

from gmft.detectors.tatr import TATRDetector
from gmft.auto import AutoTableFormatter


def test_tiny_df(doc_tiny):
    detector = TATRDetector()
    tables = []
    for page in doc_tiny:
        tables.extend(detector.extract(page))

    assert len(tables) == 1
    table = tables[0]
    formatter = AutoTableFormatter()
    ft = formatter.extract(table)

    expected = pd.DataFrame(
        {
            "Name": ["Water Freezing Point", "Water Boiling Point", "Body Temperature"],
            "Celsius": ["0", "100", "37"],
            "Fahrenheit": ["32", "212", "98.6"],
        }
    )

    assert_frame_equal(expected, ft.df())
