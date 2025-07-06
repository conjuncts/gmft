from dataclasses import dataclass
from typing import List, Optional


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

    table_array: List[List[Optional[str]]]

    # indices of special rows
    header_rows: List[int]
    projected_rows: List[int]
    empty_rows: List[int]

    partitions: Partitions

