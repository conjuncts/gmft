from gmft.core._dataclasses import removed_property
from gmft.formatters.histogram import HistogramConfig

from dataclasses import dataclass, field
from typing import Literal, Union


@dataclass
class DITRFormatConfig(HistogramConfig):
    """
    Configuration for :class:`.DITRTableFormatter`.
    """

    # ---- model settings ----

    warn_uninitialized_weights: bool = False
    image_processor_path: str = (
        "microsoft/table-transformer-structure-recognition-v1.1-all"
    )
    formatter_path: str = "conjuncts/ditr-e15"
    # no_timm: bool = True # use a model which uses AutoBackbone.
    torch_device: Union[Literal["auto", "cpu", "cuda"], str] = "auto"

    verbosity: int = 1
    """
    0: errors only\n
    1: print warnings\n
    2: print warnings and info\n
    3: print warnings, info, and debug
    """

    formatter_base_threshold: float = 0.3
    """Base threshold for the confidence demanded of a separating line.

    Since merged rows are generally harder to deal with than empty rows, a low threshold is usually
    better, because then more separating lines are detected.
    """

    cell_required_confidence: dict = field(
        default_factory=lambda: {
            0: 0.3,  # table
            1: 0.3,  # column
            2: 0.3,  # row
            3: 0.3,  # column header
            4: 0.5,  # projected row header
            5: 0.5,  # spanning cell
            6: 99,  # no object
        }
    )
    """Confidences required (>=) for a row/column feature to be considered good. See DITRFormattedTable.id2label

    But low confidences may be better than too high confidence (see formatter_base_threshold)
    """

    # ---- df() settings ----

    # ---- options ----

    remove_null_rows: bool = True
    """Remove rows with no text."""

    enable_multi_header: bool = True
    """Enable multi-indices in the dataframe.
    If false, then multiple headers will be merged column-wise."""

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

    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def large_table_if_n_rows_removed(self):
        pass

    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def large_table_threshold(self):
        pass

    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def large_table_row_overlap_threshold(self):
        pass

    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def force_large_table_assumption(self):
        pass

    large_table_maximum_rows: int = 1000
    """If the table predicts a large number of rows, refuse to proceed. Therefore prevent memory issues for super small text."""

    # ---- rejection and warnings ----

    # note that the overlap metric is not useful anymore since separating lines are not
    # supposed to cover the entire table.

    # hence nms is also not useful anymore.

    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def total_overlap_reject_threshold(self):
        pass

    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def total_overlap_warn_threshold(self):
        pass

    @removed_property("Overlap (nms) ({name}) is not used for the DITR model.")
    def nms_warn_threshold(self):
        pass

    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def iob_reject_threshold(self):
        pass

    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def iob_warn_threshold(self):
        pass

    # ---- technical ----

    _nms_overlap_threshold: float = 0.1
    _nms_overlap_threshold_larger: float = 0.5

    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def _large_table_merge_distance(self):
        pass

    _smallest_supported_text_height: float = 0.1
    """The smallest supported text height. Text smaller than this height will be ignored. 
    Helps prevent very small text from creating huge arrays under large table assumption."""

    # ---- deprecated ----
    # aggregate_spanning_cells = False
    @removed_property
    def aggregate_spanning_cells(self):
        pass

    # corner_clip_outlier_threshold = 0.1
    # """"corner clip" is when the text is clipped by a corner, and not an edge"""
    @removed_property
    def corner_clip_outlier_threshold(self):
        pass

    # spanning_cell_minimum_width = 0.6
    @removed_property
    def spanning_cell_minimum_width(self):
        pass

    @property
    def deduplication_iob_threshold(self):
        pass
