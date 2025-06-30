# Multi-headers
from dataclasses import dataclass
from typing import Literal
from gmft.reformat.instruction import BaseInstruction


@dataclass(frozen=True)
class TopHeaderInstruction(BaseInstruction):
    """
    Instruction to either split/merge the top header of a table
    """

    action: Literal["split", "merge", "normalize"]
