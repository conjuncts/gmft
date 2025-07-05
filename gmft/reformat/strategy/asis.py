from dataclasses import dataclass
from typing import ClassVar

from gmft.reformat.strategy import StrategySettings


@dataclass
class AsisSettings(StrategySettings):
    strategy: ClassVar[str] = "asis"
