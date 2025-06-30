from dataclasses import dataclass
from typing import Literal
from gmft.reformat.instruction import BaseInstruction


@dataclass(frozen=True)
class LeftHeaderInstruction(BaseInstruction):
    """
    Instruction to either split/merge the left header of a table
    """

    action: Literal["normalize"]
