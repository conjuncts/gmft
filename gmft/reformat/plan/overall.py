from typing import Callable, Literal, Optional, Union, overload
from typing_extensions import Self
from gmft.reformat.instruction import BaseInstruction
from gmft.reformat.instruction.filter.do_when import (
    ExcludeWhenInstruction,
    RaiseWhenInstruction,
)
from gmft.reformat.instruction.filter.threshold_predictions import (
    PredictionFilterInstruction,
)
from gmft.reformat.instruction.standard import ExecutorInstruction, VerbosityInstruction
from gmft.reformat.instruction.strategy import StrategyInstruction
from gmft.reformat.plan.base import BasePlan
from gmft.reformat.plan.split_merge import SplitMergePlan
from gmft.reformat.strategy.asis import AsisSettings
from gmft.reformat.strategy.hybrid import HybridSettings
from gmft.reformat.strategy.lta import LTASettings


class OverallPlan(SplitMergePlan):
    def __init__(
        self,
        previous: Optional[BasePlan] = None,
        instruction: Optional[BaseInstruction] = None,
        SelfCls: Optional[Callable[..., "OverallPlan"]] = None,
    ):
        """
        Constructs an OverallPlan instance.
        """
        if SelfCls is None:
            SelfCls = OverallPlan
        return super().__init__(
            previous=previous,
            instruction=instruction,
            SelfCls=SelfCls,
        )

    def with_verbosity(self, verbosity: int) -> Self:
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
    ) -> Self:
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

    def with_strategy(
        self,
        strategy: Union[
            Literal["asis", "lta", "hybrid"], AsisSettings, LTASettings, HybridSettings
        ],
    ) -> Self:
        """
        Set strategy.

        :param strategy: The strategy to use. Can be one of "asis", "lta", or "hybrid".
        Alternatively, a strategy settings object can be provided directly.
        """

        if isinstance(strategy, str):
            strategy_type = strategy
            if strategy_type not in [
                "asis",
                "lta",
                "hybrid",
            ]:
                raise ValueError(
                    f"Unrecognized strategy: {strategy_type}. "
                    "Expected 'asis', 'lta', or 'hybrid'."
                )
            assert strategy_type in [
                "asis",
                "lta",
                "hybrid",
            ], (
                f"Invalid strategy: {strategy_type}. Valid strategies are: ['asis', 'lta', 'hybrid']"
            )
            settings = None
        else:
            if isinstance(strategy, AsisSettings):
                strategy_type = "asis"
            elif isinstance(strategy, LTASettings):
                strategy_type = "lta"
            elif isinstance(strategy, HybridSettings):
                strategy_type = "hybrid"
            else:
                raise ValueError(
                    f"Unrecognized strategy: {strategy_type}. "
                    "Expected AsisSettings, LTASettings, or HybridSettings."
                )
            settings = strategy

        return OverallPlan(
            previous=self,
            instruction=StrategyInstruction(strategy=strategy, settings=settings),
        )

    def with_executor(self, executor_type: Literal["standard"]) -> Self:
        """
        Set the executor type for the plan.

        :param executor_type: The type of executor to use.
        :return: The updated OverallPlan instance.
        """
        if executor_type != "standard":
            raise ValueError(f"Invalid executor type: {executor_type}")

        return OverallPlan(
            previous=self,
            instruction=ExecutorInstruction(executor_type=executor_type),
        )
