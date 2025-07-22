from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

import polars as pl

from gmft.algorithm.dividers import find_column_for_target, find_row_for_target
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

    spanning: List[tuple[float, float, float, float]]
    "Regions with spanning cells"


@dataclass
class FormatState:
    """
    Describes the formatting of a table.

    [Experimental] Subject to change without notice.
    """

    partitions: Partitions

    words: WordsList

    # table_array: List[List[Optional[str]]]

    # indices of special rows
    header_rows: List[int]
    projected_rows: List[int]
    empty_rows: List[int]
