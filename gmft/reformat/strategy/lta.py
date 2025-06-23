from dataclasses import dataclass
from gmft.reformat.strategy import StrategySettings


@dataclass
class LargeTableSettings(StrategySettings):
    """
    Settings for the large table assumption (LTA) strategy.
    """


    large_table_maximum_rows: int = 1000
    """If the table predicts a large number of rows, refuse to proceed. Therefore prevent memory issues for super small text."""

    _large_table_merge_distance: float = 0.6
    """In the large_table method, if two means are within (60% * text_height) of each other, then they are merged.
    This may be useful to adjust if text is being split due to subscripts/superscripts."""

