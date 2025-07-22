from typing import Callable, List, Literal, Optional, Union
from typing_extensions import Self
from gmft.reformat._instruction import BaseInstruction
from gmft.reformat._instruction.split_merge.drop import DropNullsInstruction
from gmft.reformat._instruction.split_merge.header import (
    LeftHeaderInstruction,
    TopHeaderInstruction,
)
from gmft.reformat._plan.base import BasePlan


class SplitMergePlan(BasePlan):
    """
    SplitMergePlan is a specialized plan for handling split and merge operations.

    Once the first split/merge instruction is given,
    overall settings (such as verbosity) can no longer be set.

    Hence, split/merge instructions should come last.
    See the documentation for more details.
    """

    def __init__(
        self,
        previous: Optional[BasePlan] = None,
        instruction: Optional[BaseInstruction] = None,
        SelfCls: Optional[Callable[..., "SplitMergePlan"]] = None,
    ):
        if SelfCls is None:
            SelfCls = SplitMergePlan
        return super().__init__(
            previous=previous,
            instruction=instruction,
            SelfCls=SelfCls,
        )

    def drop_nulls(self) -> "SplitMergePlan":
        """
        Remove rows with no text.

        :return: The updated **SplitMergePlan** instance.
        """
        return SplitMergePlan(previous=self, instruction=DropNullsInstruction())

    def normalize_left_header(
        self,
        on: Union[List[int], Literal["auto"]] = "auto",
        how: Literal["algorithm", "deep"] = "algorithm",
    ) -> "SplitMergePlan":
        """
        Normalize hierarchical left headers.

        That is, for headers (often on the left) which span multiple rows, the value will be
        repeated for each row.

        :param on: Indices of columns to normalize. If "auto", columns will be detected automatically.
        :param how: Method of normalization.
            - "algorithm": Assumes that left headers have text at the top of the cell,
                and are padded downwards with whitespace.
            - "deep" uses the predictions from Table Transformer.

        :return: The updated **SplitMergePlan** instance.
        """
        return SplitMergePlan(
            previous=self, instruction=LeftHeaderInstruction(action="normalize")
        )

    def normalize_top_header(self) -> "SplitMergePlan":
        """
        Normalize the top header of a table.

        That is, the value of semantic spanning cells will be
        repeated for each column.

        :return: The updated **SplitMergePlan** instance.
        """
        return SplitMergePlan(
            previous=self, instruction=TopHeaderInstruction(action="normalize")
        )

    def max_top_headers(self, limit: Literal[1, None, "inf"]) -> "SplitMergePlan":
        """
        Limit the number of top headers to a maximum of `limit`.

        :param limit: The maximum number of top headers. Either 1, None (no limit), or 'inf' (no limit).

        :return: The updated **SplitMergePlan** instance.
        """
        return SplitMergePlan(
            previous=self, instruction=TopHeaderInstruction(action="max one")
        )

    def normalize_spans(self) -> "SplitMergePlan":
        """
        Normalize the semantic spanning cells in the table.

        That is, the values of semantic spanning cells
        are repeated for each row or column as appropriate.

        :return: The updated **SplitMergePlan** instance.
        """
        return SplitMergePlan(
            previous=self, instruction=LeftHeaderInstruction(action="normalize spans")
        )
