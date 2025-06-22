from typing import Optional, Tuple, TypedDict, List, Union
from typing_extensions import NotRequired


# Type definitions for predictions structure
class RawBboxPredictions(TypedDict):
    """Type definition for a single model's bbox prediction output."""

    scores: List[float]
    labels: List[int]
    boxes: List[List[float]]


class BboxPrediction(TypedDict):
    confidence: float
    label: str
    bbox: Tuple[float, float, float, float]


class EffectivePredictions(TypedDict):
    """
    Effective rows/columns/etc as seen by the image --> df algorithm.

    May be postprocessed from the table structure recognition model of choice (ie. TATR).
    """

    rows: List[BboxPrediction]

    columns: List[BboxPrediction]

    headers: List[BboxPrediction]

    projecting: List[BboxPrediction]
    "Projected rows as seen by the image --> df algorithm."

    spanning: List[BboxPrediction]
    "Spanning cells as seen by the image --> df algorithm."


class IndicesPredictions(TypedDict):
    """
    Indices of key rows/columns, such as: top header, projecting, hier_left.
    """

    _top_header: NotRequired[List[int]]
    _projecting: NotRequired[List[int]]
    _hier_left: NotRequired[List[int]]


class TablePredictions(TypedDict):
    """Type definition for the complete predictions dictionary."""

    tatr: RawBboxPredictions

    effective: EffectivePredictions
    indices: IndicesPredictions


def _empty_effective_predictions():
    return {
        "rows": [],
        "columns": [],
        "headers": [],
        "projecting": [],
        "spanning": [],
    }


def _empty_indices_predictions():
    return {}


# predictions: Predictions = {
#     "tatr": {
#         "scores": [
#             0.9999045133590698,
#             0.9998310804367065,
#             0.9999147653579712,
#             0.9998205304145813,
#             0.9999688863754272,
#             0.9998650550842285,
#             0.9998096823692322,
#             0.9897574186325073,
#             0.9998759031295776,
#         ],
#         "labels": [2, 2, 1, 2, 1, 1, 2, 3, 0],
#         "boxes": [
#             [
#                 71.36495971679688,
#                 159.0726318359375,
#                 797.0186767578125,
#                 206.53753662109375,
#             ],
#             [
#                 70.94971466064453,
#                 110.53954315185547,
#                 797.128173828125,
#                 158.9207000732422,
#             ],
#             [71.17463684082031, 73.58935546875, 329.6531677246094, 244.5222625732422],
#             [71.1388931274414, 73.6107177734375, 797.3575439453125, 109.99236297607422],
#             [331.3564147949219, 73.64269256591797, 576.944091796875, 244.3546905517578],
#             [
#                 575.6424560546875,
#                 73.62675476074219,
#                 797.5115356445312,
#                 244.22035217285156,
#             ],
#             [71.27164459228516, 206.5450439453125, 796.82958984375, 244.68435668945312],
#             [
#                 71.13404083251953,
#                 73.61981964111328,
#                 797.3654174804688,
#                 109.93215942382812,
#             ],
#             [71.12321472167969, 73.54254150390625, 797.08642578125, 244.42941284179688],
#         ],
#     }
# }
