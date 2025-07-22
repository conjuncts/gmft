from dataclasses import dataclass
from gmft.reformat._instruction import BaseInstruction
from gmft.impl.tatr.config import TATRFormatConfig


@dataclass
class LegacyTATRInstruction(BaseInstruction):
    """
    Reformats with the legacy TATR config.
    """

    config: TATRFormatConfig
