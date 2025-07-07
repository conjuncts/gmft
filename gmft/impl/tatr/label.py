from dataclasses import dataclass

from gmft.core.ml.prediction import BboxPrediction


class TATRLabel:
    """
    Enum for the labels used by the Table Transformer.
    """

    _POSSIBLE_ROWS = [
        "table row",
        "table spanning cell",
        "table projected row header",
    ]  # , 'table column header']
    _POSSIBLE_PROJECTING_ROWS = [
        "table projected row header"
    ]  # , 'table spanning cell']
    _POSSIBLE_COLUMN_HEADERS = ["table column header"]
    _POSSIBLE_COLUMNS = ["table column"]
    id2label = {
        0: "table",
        1: "table column",
        2: "table row",
        3: "table column header",
        4: "table projected row header",
        5: "table spanning cell",
        6: "no object",
    }
    label2id = {v: k for k, v in id2label.items()}
