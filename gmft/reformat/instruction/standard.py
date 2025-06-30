from dataclasses import dataclass
from typing import Literal
from abc import ABC

from gmft.reformat.instruction import BaseInstruction


@dataclass(frozen=True)
class EngineInstruction(BaseInstruction):
    """
    Reformat with a specific engine.
    """

    engine_type: Literal["standard"]


@dataclass(frozen=True)
class VerbosityInstruction(BaseInstruction):
    """
    Reformat with a specific verbosity level.
    """

    verbosity: int
