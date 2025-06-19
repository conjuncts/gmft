import torch


from dataclasses import dataclass, field
from typing import Literal, Union


@dataclass
class TATRFormatConfig:
    """
    Configuration for :class:`.TATRTableFormatter`.
    """

    # ---- model settings ----

    warn_uninitialized_weights: bool = False
    image_processor_path: str = "microsoft/table-transformer-detection"
    formatter_path: str = "microsoft/table-transformer-structure-recognition"
    no_timm: bool = True  # use a model which uses AutoBackbone.
    torch_device: str = "cuda" if torch.cuda.is_available() else "cpu"
    # https://huggingface.co/microsoft/table-transformer-structure-recognition/discussions/5
    # "microsoft/table-transformer-structure-recognition-v1.1-all"

    verbosity: int = 1
    """
    0: errors only\n
    1: print warnings\n
    2: print warnings and info\n
    3: print warnings, info, and debug
    """

    formatter_base_threshold: float = 0.3
    """Base threshold for the confidence demanded of a table feature (row/column).
    Note that a low threshold is actually better, because overzealous rows means that
    generally, numbers are still aligned and there are just many empty rows
    (having fewer rows than expected merges cells, which is bad).
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
    """Confidences required (>=) for a row/column feature to be considered good. See TATRFormattedTable.id2label

    But low confidences may be better than too high confidence (see formatter_base_threshold)
    """

    # ---- df() settings ----

    # ---- options ----

    remove_null_rows: bool = True
    """Remove rows with no text."""

    enable_multi_header: bool = False
    """Enable multi-indices in the dataframe.
    If false, then multiple headers will be merged column-wise."""

    semantic_spanning_cells: bool = False
    """
    [Experimental] Enable semantic spanning cells, which often encode hierarchical multi-level indices.
    """

    semantic_hierarchical_left_fill: Literal["algorithm", "deep", None] = "algorithm"
    """
    [Experimental] When semantic spanning cells is enabled, when a left header is detected which might
    represent a group of rows, that same value is reduplicated for each row.
    Possible values: 'algorithm', 'deep', None.

    'algorithm': assumes that the higher-level header is always the first row followed by several empty rows.\n
    'deep': merges headers according to the spanning cells detected by the Table Transformer.\n
    None: headers are not duplicated.
    """

    # ---- large table ----

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

    large_table_maximum_rows: int = 1000
    """If the table predicts a large number of rows, refuse to proceed. Therefore prevent memory issues for super small text."""

    force_large_table_assumption: Union[bool, None] = None
    """True: force large table assumption to be applied to all tables.\n
    False: force large table assumption to not be applied to any tables.\n
    None: heuristically apply large table assumption according to threshold and overlap"""

    # ---- rejection and warnings ----

    total_overlap_reject_threshold: float = 0.9
    """Reject if total overlap is > 90% of table area."""

    total_overlap_warn_threshold: float = 0.1
    """Warn if total overlap is > 10% of table area."""

    nms_warn_threshold: int = 5
    """Warn if non maxima suppression removes > 5 rows."""

    iob_reject_threshold: float = 0.05
    """Reject if iob between textbox and cell is < 5%."""

    iob_warn_threshold: float = 0.5
    """Warn if iob between textbox and cell is < 50%."""

    # ---- technical ----

    _nms_overlap_threshold: float = 0.1
    """Non-maxima suppression: if two rows overlap by > threshold (default: 10%), then the one with the lower confidence is removed.
    A subsequent technique is able to fill in gaps created by NMS."""

    _large_table_merge_distance: float = 0.6
    """In the large_table method, if two means are within (60% * text_height) of each other, then they are merged.
    This may be useful to adjust if text is being split due to subscripts/superscripts."""

    _smallest_supported_text_height: float = 0.1
    """The smallest supported text height. Text smaller than this height will be ignored. 
    Helps prevent very small text from creating huge arrays under large table assumption."""

    # ---- deprecated ----
    # aggregate_spanning_cells = False
    @property
    def aggregate_spanning_cells(self):
        raise DeprecationWarning(
            "aggregate_spanning_cells has been removed. Will break in v0.6.0."
        )

    @aggregate_spanning_cells.setter
    def aggregate_spanning_cells(self, value):
        raise DeprecationWarning(
            "aggregate_spanning_cells has been removed. Will break in v0.6.0."
        )

    # corner_clip_outlier_threshold = 0.1
    # """"corner clip" is when the text is clipped by a corner, and not an edge"""
    @property
    def corner_clip_outlier_threshold(self):
        raise DeprecationWarning(
            "corner_clip_outlier_threshold has been removed. Will break in v0.6.0."
        )

    @corner_clip_outlier_threshold.setter
    def corner_clip_outlier_threshold(self, value):
        raise DeprecationWarning(
            "corner_clip_outlier_threshold has been removed. Will break in v0.6.0."
        )

    # spanning_cell_minimum_width = 0.6
    @property
    def spanning_cell_minimum_width(self):
        raise DeprecationWarning(
            "spanning_cell_minimum_width has been removed. Will break in v0.6.0."
        )

    @spanning_cell_minimum_width.setter
    def spanning_cell_minimum_width(self, value):
        raise DeprecationWarning(
            "spanning_cell_minimum_width has been removed. Will break in v0.6.0."
        )

    @property
    def deduplication_iob_threshold(self):
        raise DeprecationWarning(
            "deduplication_iob_threshold is deprecated. See nms_overlap_threshold instead. Will break in v0.6.0."
        )

    @deduplication_iob_threshold.setter
    def deduplication_iob_threshold(self, value):
        raise DeprecationWarning(
            "deduplication_iob_threshold is deprecated. See nms_overlap_threshold instead. Will break in v0.6.0."
        )
