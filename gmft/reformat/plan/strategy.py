from gmft.reformat.instruction.strategy import (
    SettingsInstruction,
    StrategyInstruction,
)
from gmft.reformat.plan import BasePlan
from gmft.reformat.strategy.asis import AsisSettings
from gmft.reformat.strategy.hybrid import HybridSettings
from gmft.reformat.strategy.lta import LTASettings


class AsisPlan(BasePlan):
    def __init__(
        self, previous: BasePlan, instruction: StrategyInstruction, overall_plan_cls
    ):
        """
        Initialize the AsisPlan with an optional previous plan.

        :param previous: The previous plan to build upon, if any.
        :param overall_plan_cls: The class of the overall plan to be used.
        """
        super().__init__(previous=previous, instruction=instruction)
        self.overall_plan_cls = overall_plan_cls  # OverallPlan needs to be passed in, to prevent a circular import

    def with_strategy_settings(self, settings: AsisSettings) -> "AsisPlan":
        """
        Set the strategy settings for the plan.

        :param strategy_settings: The strategy settings to apply.
        :return: The updated AsisPlan instance.
        """
        return self.overall_plan_cls(
            previous=self,
            instruction=SettingsInstruction(strategy="asis", settings=settings),
        )


class LTAPlan(BasePlan):
    def __init__(
        self, previous: BasePlan, instruction: StrategyInstruction, overall_plan_cls
    ):
        """
        Initialize the LTAPlan with an optional previous plan.

        :param previous: The previous plan to build upon, if any.
        :param instruction: The instruction to be used for the plan.
        :param overall_plan_cls: The class of the overall plan to be used.
        """
        super().__init__(previous=previous, instruction=instruction)
        self.overall_plan_cls = overall_plan_cls  # OverallPlan needs to be passed in, to prevent a circular import

    def with_strategy_settings(self, settings: LTASettings) -> "LTAPlan":
        """
        Set the strategy settings for the plan.

        :param strategy_settings: The strategy settings to apply.
        :return: The updated LTAPlan instance.
        """
        return self.overall_plan_cls(
            previous=self,
            instruction=SettingsInstruction(strategy="lta", settings=settings),
        )


class HybridPlan(BasePlan):
    def __init__(
        self, previous: BasePlan, instruction: StrategyInstruction, overall_plan_cls
    ):
        """
        Initialize the HybridPlan with an optional previous plan.

        :param previous: The previous plan to build upon, if any.
        :param instruction: The instruction to be used for the plan.
        :param overall_plan_cls: The class of the overall plan to be used.
        """
        super().__init__(previous=previous, instruction=instruction)
        self.overall_plan_cls = overall_plan_cls  # OverallPlan needs to be passed in, to prevent a circular import

    def with_strategy_settings(self, settings: HybridSettings) -> "HybridPlan":
        """
        Set the strategy settings for the plan.

        :param strategy_settings: The strategy settings to apply.
        :return: The updated HybridPlan instance.
        """
        return self.overall_plan_cls(
            previous=self,
            instruction=SettingsInstruction(strategy="hybrid", settings=settings),
        )
