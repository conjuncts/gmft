from dataclasses import dataclass

from gmft.reformat.instruction import BaseInstruction


@dataclass(frozen=True)
class DropNullsInstruction(BaseInstruction):
    """
    Instruction to drop rows with no text.
    """
