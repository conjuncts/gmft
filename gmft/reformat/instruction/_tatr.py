from gmft.reformat.instruction import BaseInstruction
from gmft.impl.tatr.config import TATRFormatConfig


class LegacyTATRFormatInstruction(BaseInstruction):
    """
    A "LegacyTATRFormatInstruction" is a legacy reformat instruction.
    """

    def __init__(self, config: TATRFormatConfig):
        self.config = config
