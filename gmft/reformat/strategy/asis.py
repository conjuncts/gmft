from dataclasses import dataclass
from typing import ClassVar

from gmft.reformat.strategy import StrategySettings


@dataclass
class AsisSettings(StrategySettings):
    strategy: ClassVar[str] = "asis"

    foo: str = "bar"


print(
    AsisSettings(foo="baz")
)  # Example usage to show that the class can be instantiated
