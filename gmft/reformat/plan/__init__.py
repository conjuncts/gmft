from gmft.reformat.instruction import BaseInstruction


class BasePlan:
    """
    Base class for plans (intermediate stages of reformatting).

    Only instructions are stored, not the table itself (so tables are populated only when needed).

    Plans are stored as a linked-list, allowing easy branching.
    """

    def __init__(self, previous: "BasePlan", instruction: BaseInstruction):
        """
        Initialize the BasePlan with a previous plan and an instruction.

        :param previous: The previous plan in the chain.
        :param instruction: The instruction associated with this plan.
        """
        self.previous = previous
        self.instruction = instruction
