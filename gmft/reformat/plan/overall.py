from typing import Literal, Optional, Union, overload
from gmft.reformat.instruction.filter.threshold_predictions import (
    PredictionFilterInstruction,
)
from gmft.reformat.instruction.standard import VerbosityInstruction
from gmft.reformat.instruction.strategy import SettingsInstruction, StrategyInstruction
from gmft.reformat.plan.split_merge import SplitMergePlan
from gmft.reformat.strategy import StrategySettings
from gmft.reformat.strategy.asis import AsisSettings
from gmft.reformat.strategy.hybrid import HybridSettings
from gmft.reformat.strategy.lta import LTASettings
from gmft.reformat.plan.strategy import AsisPlan, LTAPlan, HybridPlan


class OverallPlan(SplitMergePlan):
    def with_verbosity(self, verbosity: int) -> "OverallPlan":
        """
        Set the verbosity level for the plan.

        :param verbosity: The verbosity level to set.
        :return: The updated OverallPlan instance.
        """
        return OverallPlan(
            previous=self, instruction=VerbosityInstruction(verbosity=verbosity)
        )

    def filter_predictions(
        self,
        formatter_base_threshold: float,
        cell_required_confidence: dict = None,
        _nms_overlap_threshold: float = 0.1,
    ) -> "OverallPlan":
        """
        Filter predictions based on a given threshold.

        :param threshold: The threshold value for filtering predictions.
        :param cell_required_confidence: A dictionary mapping cell types to their required confidence levels.

        These are the cell types:
            - 0: table
            - 1: column
            - 2: row
            - 3: column header
            - 4: projected row header
            - 5: spanning cell
            - 6: no object

        :param _nms_overlap_threshold: Cells overlapping >= threshold are pruned during non-maximum suppression.
        :return: The updated OverallPlan instance.
        """
        if cell_required_confidence is None:
            cell_required_confidence = {
                0: 0.3,  # table
                1: 0.3,  # column
                2: 0.3,  # row
                3: 0.3,  # column header
                4: 0.5,  # projected row header
                5: 0.5,  # spanning cell
                6: 99,  # no object
            }

        return OverallPlan(
            previous=self,
            instruction=PredictionFilterInstruction(
                formatter_base_threshold=formatter_base_threshold,
                cell_required_confidence=cell_required_confidence,
                _nms_overlap_threshold=_nms_overlap_threshold,
            ),
        )

    @overload
    def with_strategy(
        self, strategy: Union[Literal["asis"], AsisSettings] = None
    ) -> "OverallPlan": ...

    @overload
    def with_strategy(
        self, strategy: Union[Literal["lta"], LTASettings] = None
    ) -> "OverallPlan": ...

    @overload
    def with_strategy(
        self, strategy: Union[Literal["hybrid"], HybridSettings] = None
    ) -> "OverallPlan": ...

    def with_strategy(
        self,
        strategy: Union[
            Literal["asis", "lta", "hybrid"], AsisSettings, LTASettings, HybridSettings
        ],
    ) -> "OverallPlan":
        """
        Set strategy.

        :param strategy: The strategy to use. Can be one of "asis", "lta", or "hybrid".
        Alternatively, a strategy settings object can be provided directly.
        """
        valid_strategies = {
            "asis": AsisSettings,
            "lta": LTASettings,
            "hybrid": HybridSettings,
        }
        valid_plans = {
            "asis": AsisPlan,
            "lta": LTAPlan,
            "hybrid": HybridPlan,
        }
        strat_type_instr = StrategyInstruction(strategy=strategy)

        if settings is not None:
            # Settings ARE available. Do both steps.
            intermed = OverallPlan(previous=self, instruction=strat_type_instr)

            settings_cls = valid_strategies[strategy]
            assert isinstance(settings, settings_cls)
            return OverallPlan(
                previous=intermed,
                instruction=SettingsInstruction(strategy=strategy, settings=settings),
            )
        else:
            # No settings available.
            # Need a two-step process. Only do the first step. (No settings provided)
            # Pass OverallPlan to prevent circular import
            if strategy not in valid_plans:
                raise ValueError(
                    f"Invalid strategy: {strategy}. Valid strategies are: {list(valid_plans.keys())}"
                )

            return valid_plans[strategy](
                previous=self,
                instruction=strat_type_instr,
                overall_plan_cls=OverallPlan,
            )
