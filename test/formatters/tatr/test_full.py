import json
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
    ft.df().to_csv("data/test/outputs/actual/tiny_df.csv", index=False)
    with open("data/test/outputs/actual/tiny_df.info", "w") as f:
        # ft.to_dict()
        json.dump(ft.to_dict(), f, indent=4)
