import json
from typing import List
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from gmft.detectors.base import CroppedTable
from gmft.detectors.tatr import TATRDetector
from gmft.auto import AutoTableFormatter
from gmft.pdf_bindings.base import ImageOnlyPage


def test_tiny_df(doc_tiny):
    detector = TATRDetector()
    tables: List[CroppedTable] = []
    for page in doc_tiny:
        tables.extend(detector.extract(page))

    assert len(tables) == 1
    table = tables[0]
    assert table.bbox == pytest.approx((76.6, 162.8, 441.0, 248.7), abs=5.0)

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


def test_tiny_df_image_only(doc_tiny):
    detector = TATRDetector()

    tables = detector.extract(ImageOnlyPage.from_page(doc_tiny[0], dpi=144))
    assert len(tables) == 1

    assert tables[0].bbox == pytest.approx((76.6, 162.8, 441.0, 248.7), abs=5.0)

    formatter = AutoTableFormatter()
    ft = formatter.extract(tables[0])
    actual = ft.df()
    # ft.visualize().save("test_tiny_df_image_only.png")
    expected = pd.DataFrame(
        {
            "Name": ["Water Freezing Point", "Water Boiling Point", "Body Temperature"],
            "Celsius": ["0", "100", "37"],
            "Fahrenheit": ["32", "212", "98.6"],
        }
    )

    assert_frame_equal(expected, actual)
