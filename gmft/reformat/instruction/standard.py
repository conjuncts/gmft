from dataclasses import dataclass
from typing import Any, Literal
from abc import ABC

from gmft.reformat.instruction import BaseInstruction


@dataclass(frozen=True)
class ExecutorInstruction(BaseInstruction):
    """
    Reformat with a specific executor.
    """

    executor_type: Literal["standard"]


@dataclass(frozen=True)
class PassiveInstruction(BaseInstruction):

    key: Literal["verbosity", "executor"]
    value: Any

@dataclass(frozen=True)
class VerbosityInstruction(BaseInstruction):
    """
    Reformat with a specific verbosity level.
    """

    verbosity: int
