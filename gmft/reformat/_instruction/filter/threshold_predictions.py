from dataclasses import dataclass, field
from gmft.reformat._instruction import BaseInstruction


@dataclass(frozen=True)
class PredictionFilterInstruction(BaseInstruction):
    """
    Filter predictions based on a given threshold.
    """

    formatter_base_threshold: float
    cell_required_confidence: dict
    _nms_overlap_threshold: float
