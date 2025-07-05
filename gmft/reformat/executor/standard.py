from gmft.formatters.base import FormattedTable
from gmft.reformat.plan.overall import OverallPlan


class StandardReformatExecutor:
    """
    Standard reformat executor.
    Responsible for processing and applying reformat instructions.
    """

    def __init__(self, config):
        self.config = config

    def reformat(self, data):
        """
        Reformat the given data according to the standard GMFT format.

        :param data: The data to be reformatted.
        :return: Reformatted data.
        """
        # Implement the reformatting logic here
        # For now, we will just return the data as is
        return data


def _collect_instructions(plan):
    """
    Collect all instructions from the plan and its previous plans.

    :param plan: The plan to collect instructions from.
    :return: A list of instructions.
    """
    instructions = []
    current_plan = plan
    while current_plan:
        if current_plan.instruction:
            instructions.append(current_plan.instruction)
        current_plan = current_plan.previous
    return instructions[::-1]  # Reverse to maintain order from first to last

def _execute_plan(plan):
    instructions = _collect_instructions(plan)

    # plan can be split into two categories:
    # 1. passive (order doesn't matter, only the last instruction )

    # 2. active (order matters)

    pass



class _InitialPlan(OverallPlan):
    """
    Initial plan for reformatting.
    This is the starting point of the reformatting chain.
    """

    def __init__(self, ft: FormattedTable):
        super().__init__(previous=None, instruction=None)
        self.ft = ft


def _reformat(ft) -> OverallPlan:
    """
    Begin reformat chain.
    """
    return _InitialPlan(ft=ft)

