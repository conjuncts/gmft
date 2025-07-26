from dataclasses import dataclass
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Union

from gmft.algorithm.dividers import find_column_for_target, find_row_for_target
from gmft.core.ml.prediction import BboxPrediction
from gmft.core.schema import WordMetadata
from gmft.core.words_list import WordsList

if TYPE_CHECKING:
    from gmft.detectors.base import CroppedTable


@dataclass
class Partitions:
    """
    Most concise table definition.
    """

    row_dividers: List[float]
    """y values where table gets partitioned into rows."""

    col_dividers: List[float]
    """x values where table gets partitioned into columns."""

    top_header_y: float
    """y value which separates the top header from the rest of the table."""

    left_header_x: float
    """x value which separates the left header from the rest of the table."""

    projected: List[tuple[float, float, float, float]]
    "Regions with projected rows"

    # spanning: List[tuple[float, float, float, float]]
    spanning: List[BboxPrediction]
    "Regions with spanning cells. Confidences is required for NMS."


class CellMergerType(NamedTuple):
    """
    [Experimental] exact values of enum not guaranteed.
    """

    NONE = 0
    "Cell merger, but no action to be taken."

    REPEAT = 1
    """The same value will be repeated throughout the range.

    If unset, text is guaranteed to appear only once.
    """

    AGGREGATE = 2
    "Text from the range should be combined together. Can be combined with REPEAT or PUSH_x."

    PUSH_FORWARD = 4
    """
    Currently only defined for 1xn or nx1 ranges.
    (In the future, could be generalized by acting on the longer axis.)

    Exactly one of AGGREGATE, REPEAT must be set.

    If AGGREGATE is set, the range is emptied
    and all text is combined and placed in the last cell.
    
    If REPEAT is set, an empty cell at position i is filled with text from i-1.

    If both are unset: undefined.
    """

    PUSH_BACKWARD = 8
    "Same as PUSH_FORWARD, but in the opposite direction. See caveats of PUSH_FORWARD."

    FILL_UNIQUE = 16
    "Expect the range to only have one non-empty cell. Stop once a second non-empty cell is encountered."

    """
    Begin specific types
    
    """
    # 2 is reserved for future use

    LEFT_HIER = 32
    "For cells merged as left hierarchical headers"

    TOP_HIER = 64
    "For cells merged as top hierarchical headers"

    TOP_NONHIER = 128
    """A non-hierarchical column header -- 
    eg. a title with a newline present"""


class CellMergerMetadata:
    pass


class CellMerger(NamedTuple):
    """
    Describes how multiple cells can be merged.
    The rectangular selection defined by row_min, col_min, row_max, col_max
    will be merged.
    """

    row_min: int
    col_min: int
    row_max: int
    col_max: int
    dtype: int
    """The nature of the cell merge. See CellMergerType"""
    confidence: float
    """
    Confidence of this merge.
    """
    debug: Optional[dict] = None
    """
    Debug information (optional)"""


class SpanningPrediction(BboxPrediction):
    merger: CellMerger


@dataclass
class TableStructureWithWords:
    """
    Describes the formatting of a table.

    [Experimental] Subject to change without notice.
    """

    locations: Partitions
    words: WordsList


@dataclass
class TableStructureWithArray:
    """
    Describes the formatting of a table.

    [Experimental] Subject to change without notice.
    """

    locations: Partitions
    words: WordsList
    table_array: List[List[Optional[str]]]

    # indices of special rows
    header_rows: List[int]
    projected_rows: List[int]
    empty_rows: List[int]

    merges: List[SpanningPrediction]
