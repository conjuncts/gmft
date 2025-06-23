from typing import Literal

from gmft.reformat.instruction import BaseInstruction


class EngineInstruction(BaseInstruction):
    """
    Instruction to use a specific reformatting engine.
    """

    def __init__(self, engine_type: Literal["standard"]):
        self.engine_type = engine_type

class StrategyInstruction(BaseInstruction):
    """
    Instruction to use a specific strategy.
    """

    def __init__(self, strategy: Literal["asis", "lta", "histogram"]):
        self.strategy = strategy

class VerbosityInstruction(BaseInstruction):
    """
    Instruction to set the verbosity level.
    """

    def __init__(self, verbosity: int):
        self.verbosity = verbosity
