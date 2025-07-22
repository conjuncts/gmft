from dataclasses import dataclass
from typing import Literal
from gmft.reformat._instruction import BaseInstruction


@dataclass
class ExcludeWhenInstruction(BaseInstruction):
    iob_threshold: float
    smallest_supported_text_height: float


@dataclass
class RaiseWhenInstruction(BaseInstruction):
    total_overlap_threshold: float
    nms_threshold: float
    iob_threshold: float

    warn: bool = False
    operator: Literal["AND", "OR"] = "AND"
