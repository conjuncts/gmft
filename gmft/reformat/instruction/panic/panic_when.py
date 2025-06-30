from dataclasses import dataclass
from gmft.reformat.instruction import BaseInstruction


@dataclass
class PanicInstruction(BaseInstruction):
    """
    Instruction to raise an exception or warn when a certain condition is met.
    """

    total_overlap_reject_threshold: float = 0.9
    total_overlap_warn_threshold: float = 0.1
    nms_warn_threshold: int = 5

    iob_warn_threshold: float = 0.5
    """Warn if iob between textbox and cell is < 50%."""
