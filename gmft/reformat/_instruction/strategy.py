from dataclasses import dataclass
from typing import Literal, Optional, Union

from gmft.reformat._instruction import BaseInstruction
from gmft.reformat._strategy.asis import AsisSettings
from gmft.reformat._strategy.hybrid import HybridSettings
from gmft.reformat._strategy.lta import LTASettings


@dataclass(frozen=True)
class StrategyInstruction(BaseInstruction):
    """
    Reformat with a specific strategy (with specific settings)
    """

    strategy: Literal["asis", "lta", "histogram"]
    settings: Optional[Union[AsisSettings, LTASettings, HybridSettings]]
