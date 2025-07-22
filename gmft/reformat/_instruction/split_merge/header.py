from dataclasses import dataclass
from typing import Literal
from gmft.reformat._instruction import BaseInstruction


@dataclass(frozen=True)
class LeftHeaderInstruction(BaseInstruction):
    """
    Instruction to either split/merge the left header of a table
    """

    action: Literal["normalize"]


@dataclass(frozen=True)
class TopHeaderInstruction(BaseInstruction):
    """
    Instruction to either split/merge the top header of a table
    """

    action: Literal["max one", "no max", "normalize"]
