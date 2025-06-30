from dataclasses import dataclass
from typing import Union
from gmft.reformat.strategy import StrategySettings


@dataclass
class HybridSettings(StrategySettings):
    """
    The hybrid strategy combines the large table assumption (LTA) and the as-is strategy.
    """

    large_table_if_n_rows_removed: int = 8
    """
    If >= n rows are removed due to non-maxima suppression (NMS), then this table is classified as a large table.
    """

    large_table_threshold: int = 10
    """With large tables, table transformer struggles with placing too many overlapping rows. 
    Luckily, with more rows, we have more info on the usual size of text, which we can use to make 
    a guess on the height such that no rows are merged or overlapping.

    Large table assumption is only applied when (# of rows > large_table_threshold) AND (total overlap > large_table_row_overlap_threshold). 
    Set 9999 to disable; set 0 to force large table assumption to run every time."""

    large_table_row_overlap_threshold: float = 0.2
    """With large tables, table transformer struggles with placing too many overlapping rows. 
    Luckily, with more rows, we have more info on the usual size of text, which we can use to make 
    a guess on the height such that no rows are merged or overlapping.

    Large table assumption is only applied when (# of rows > large_table_threshold) AND (total overlap > large_table_row_overlap_threshold). 
    Set 9999 to disable; set 0 to force large table assumption to run every time."""

    force_large_table_assumption: Union[bool, None] = None
    """True: force large table assumption to be applied to all tables.\n
    False: force large table assumption to not be applied to any tables.\n
    None: heuristically apply large table assumption according to threshold and overlap"""
