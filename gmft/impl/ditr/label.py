from dataclasses import dataclass

from gmft.core.ml.prediction import BboxPrediction


class DITRLabel:
    """
    Enum for the labels used by the Table Transformer.
    """

    column_divider = 1
    row_divider = 2
    top_header = 3
    projected = 4
    spanning = 0
    no_object = 6


@dataclass
class DITRLocations:
    row_dividers: list[float]
    col_dividers: list[float]
    row_divider_intervals: list[tuple[float, float]]
    col_divider_intervals: list[tuple[float, float]]

    top_headers: list[tuple[float, float, float, float]]
    projected: list[tuple[float, float, float, float]]
    spanning: list[BboxPrediction]
