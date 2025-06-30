from dataclasses import dataclass
from typing import Literal

from gmft.reformat.instruction import BaseInstruction
from gmft.reformat.strategy.asis import AsisSettings
from gmft.reformat.strategy.hybrid import HybridSettings
from gmft.reformat.strategy.lta import LTASettings


@dataclass(frozen=True)
class StrategyInstruction(BaseInstruction):
    """
    Reformat with a specific strategy.
    """

    strategy: Literal["asis", "lta", "histogram"]


@dataclass(frozen=True)
class SettingsInstruction(BaseInstruction):
    """
    Apply specific settings for the as-is strategy.
    """

    strategy: Literal["asis", "lta", "hybrid"]
    settings: AsisSettings
