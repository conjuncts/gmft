from abc import ABC
from typing import Literal
from typing_extensions import Self
from gmft.reformat.instruction.filter.do_when import (
    ExcludeWhenInstruction,
    RaiseWhenInstruction,
)


from typing import Callable, Optional
from gmft.reformat.instruction import BaseInstruction
from typing_extensions import Self


class BasePlan(ABC):
    """
    Base class for plans (intermediate stages of reformatting).

    Only instructions are stored, not the table itself (so tables are populated only when needed).

    Plans are stored as a linked-list, allowing easy branching.
    """

    def __init__(
        self: Self,
        previous: "BasePlan",
        instruction: BaseInstruction,
        SelfCls: Optional[Callable[..., Self]] = None,
    ):
        """
        Initialize the BasePlan with a previous plan and an instruction.

        :param previous: The previous plan in the chain.
        :param instruction: The instruction associated with this plan.
        """
        self.previous = previous
        self.instruction = instruction
        self.SelfCls = SelfCls

    def exclude_text_when(
        self,
        *,
        iob_threshold: float = None,
        smallest_supported_text_height: float = None,
        operator: Literal["AND", "OR"] = "AND",
    ) -> Self:
        """
        Exclude text when certain conditions are met.

        - if multiple thresholds are set, the AND condition is used.
        - multiple function calls are ORed together.

        If `exclude_text_when` is never called, then the default values are used, which are:
        `iob_threshold=0.05` and `smallest_supported_text_height=0.1`.

        :param iob_threshold:
            Skip if IOB between textbox and cell is < this number.
        :param smallest_supported_text_height:
            The smallest supported text height. Text smaller than this height will be ignored.
            Helps prevent very small text from creating huge arrays.
        """
        return self.SelfCls(
            previous=self,
            instruction=ExcludeWhenInstruction(
                iob_threshold=iob_threshold,
                smallest_supported_text_height=smallest_supported_text_height,
            ),
        )

    def raise_when(
        self,
        *,
        total_overlap_threshold=None,
        nms_threshold=None,
        iob_threshold=None,
        warn=False,
        operator: Literal["AND", "OR"] = "AND",
    ) -> Self:
        """
        Raise exception if a certain condition is met.

        - if multiple thresholds are set, the AND condition is used.
        - multiple `raise_when` calls are ORed together.

        If `raise_when` is never called, then the default values are used.

        :param total_overlap_threshold:
            Raises when total overlap > (this number) times table area.
            Suggested: 0.9
        :param nms_threshold:
            Raises when non maxima suppression removes > (this number) rows.
            Suggested: 5
        :param iob_threshold:
            Raises when any textbox and cell has an IOB < (this number).
            Suggested: 0.05

        :param warn: If True, raises a warning instead of an exception.

        """
        return self.SelfCls(
            previous=self,
            instruction=RaiseWhenInstruction(
                total_overlap_threshold=total_overlap_threshold,
                nms_threshold=nms_threshold,
                iob_threshold=iob_threshold,
                warn=warn,
            ),
        )

    def warn_when(
        self,
        *,
        total_overlap_threshold=None,
        nms_threshold=None,
        iob_threshold=None,
        operator: Literal["AND", "OR"] = "AND",
    ) -> Self:
        """
        Raise warning if a certain condition is met.

        If `warn_when` is never called, then the default values are used.

        - if multiple thresholds are set, the AND condition is used.
        - multiple `warn_when` calls are ORed together.

        """
        return self.SelfCls(
            previous=self,
            instruction=RaiseWhenInstruction(
                total_overlap_threshold=total_overlap_threshold,
                nms_threshold=nms_threshold,
                iob_threshold=iob_threshold,
                warn=True,
            ),
        )
