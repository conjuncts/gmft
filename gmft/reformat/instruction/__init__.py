from abc import ABC


class BaseInstruction(ABC):
    """
    A "BaseInstruction" is an format instruction.
    """

    pass


class FormatInstruction(BaseInstruction):
    """
    A "FormatInstruction" is a format instruction.
    """

    def __init__(self, config: dict):
        self.config = config
