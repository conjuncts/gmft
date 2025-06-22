from dataclasses import dataclass
from typing import Literal
from typing_extensions import deprecated

from gmft.formatters.histogram import HistogramConfig
from gmft.impl.tatr.config import TATRFormatConfig


@dataclass
class DITRFormatConfig(HistogramConfig, TATRFormatConfig):
    """
    Configuration for :class:`.DITRTableFormatter`.
    """

    # ---- model settings ----

    formatter_path: str = "conjuncts/ditr-e15"

    enable_multi_header: bool = True
    """Enable multi-indices in the dataframe.
    If false, then multiple headers will be merged vertically."""

    semantic_spanning_cells: bool = True
    """
    [Experimental] Enable semantic spanning cells, which often encode hierarchical multi-level indices.
    """

    semantic_hierarchical_left_fill: Literal["algorithm", "deep", None] = "deep"
    """
    [Experimental] When semantic spanning cells is enabled, when a left header is detected which might
    represent a group of rows, that same value is reduplicated for each row.
    Possible values: 'algorithm', 'deep', None.

    'algorithm': assumes that the higher-level header is always the first row followed by several empty rows.\n
    'deep': merges headers according to the spanning cells detected by the Table Transformer.\n
    None: headers are not duplicated.
    """

    # ---- large table ----

    # note that the overlap metric is not useful anymore since separating lines are not
    # supposed to cover the entire table.

    # hence nms is also not useful anymore.

    @deprecated("Large table approach ({name}) is not used for the DITR model.")
    def large_table_if_n_rows_removed(self):
        pass

    @deprecated("Large table approach ({name}) is not used for the DITR model.")
    def large_table_threshold(self):
        pass

    @deprecated("Large table approach ({name}) is not used for the DITR model.")
    def large_table_row_overlap_threshold(self):
        pass

    @deprecated("Large table approach ({name}) is not used for the DITR model.")
    def force_large_table_assumption(self):
        pass

    # ---- rejection and warnings ----

    # note that the overlap metric is not useful anymore since separating lines are not
    # supposed to cover the entire table.

    # hence nms is also not useful anymore.

    @deprecated("Overlap ({name}) is not used for the DITR model.")
    def total_overlap_reject_threshold(self):
        pass

    @deprecated("Overlap ({name}) is not used for the DITR model.")
    def total_overlap_warn_threshold(self):
        pass

    @deprecated("Overlap (nms) ({name}) is not used for the DITR model.")
    def nms_warn_threshold(self):
        pass

    @deprecated("Overlap ({name}) is not used for the DITR model.")
    def iob_reject_threshold(self):
        pass

    @deprecated("Overlap ({name}) is not used for the DITR model.")
    def iob_warn_threshold(self):
        pass

    # ---- technical ----

    _nms_overlap_threshold_larger: float = 0.5

    @deprecated("Large table approach ({name}) is not used for the DITR model.")
    def _large_table_merge_distance(self):
        pass
