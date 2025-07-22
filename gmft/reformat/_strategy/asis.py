from dataclasses import dataclass
from typing import ClassVar

from gmft.reformat._strategy import StrategySettings


@dataclass
class AsisSettings(StrategySettings):
    strategy: ClassVar[str] = "asis"
