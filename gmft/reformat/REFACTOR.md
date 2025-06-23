```python
import torch


from dataclasses import dataclass, field
from typing import Literal, Union


@dataclass
class TATRFormatConfig:

    # ---- model settings ----

    warn_uninitialized_weights: bool = False # moved to Formatter instantiation
    image_processor_path: str = "microsoft/table-transformer-detection" # moved to Formatter instantiation
    formatter_path: str = "microsoft/table-transformer-structure-recognition" # moved to Formatter instantiation
    no_timm: bool = True  # moved to Formatter instantiation
    torch_device: Union[Literal["auto", "cpu", "cuda"], str] = "auto" # moved to Formatter instantiation

    verbosity: int = 1 # with_verbosity
    """
    0: errors only\n
    1: print warnings\n
    2: print warnings and info\n
    3: print warnings, info, and debug
    """

    formatter_base_threshold: float = 0.3 # filter_predictions
    """Base threshold for the confidence demanded of a table feature (row/column).
    Note that a low threshold is actually better, because overzealous rows means that
    generally, numbers are still aligned and there are just many empty rows
    (having fewer rows than expected merges cells, which is bad).
    """

    cell_required_confidence: dict = field( # filter_predictions
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

    remove_null_rows: bool = True # drop_null_rows
    """Remove rows with no text."""

    enable_multi_header: bool = False # split_top_headers / merge_top_headers / normalize_top_headers
    """Enable multi-indices in the dataframe.
    If false, then multiple headers will be merged vertically."""

    semantic_spanning_cells: bool = False # merge_spans
    """
    [Experimental] Enable semantic spanning cells, which often encode hierarchical multi-level indices.
    """

    semantic_hierarchical_left_fill: Literal["algorithm", "deep", None] = "algorithm" # normalize_left_headers
    """
    [Experimental] When semantic spanning cells is enabled, when a left header is detected which might
    represent a group of rows, that same value is reduplicated for each row.
    Possible values: 'algorithm', 'deep', None.

    'algorithm': assumes that the higher-level header is always the first row followed by several empty rows.\n
    'deep': merges headers according to the spanning cells detected by the Table Transformer.\n
    None: headers are not duplicated.
    """

    # ---- large table ----

    large_table_if_n_rows_removed: int = 8 # hybrid strategy settings

    large_table_threshold: int = 10 # hybrid strategy settings

    large_table_row_overlap_threshold: float = 0.2 # hybrid strategy settings

    large_table_maximum_rows: int = 1000 # lta strategy settings

    force_large_table_assumption: Union[bool, None] = None # explicitly, with `.with_strategy('asis')` or `.with_strategy('lta')`

    # ---- rejection and warnings ----

    total_overlap_reject_threshold: float = 0.9 # panic_when
    total_overlap_warn_threshold: float = 0.1 # panic_when
    nms_warn_threshold: int = 5 # panic_when

    iob_reject_threshold: float = 0.05
    """Reject if iob between textbox and cell is < 5%."""

    iob_warn_threshold: float = 0.5
    """Warn if iob between textbox and cell is < 50%."""

    # ---- technical ----

    _nms_overlap_threshold: float = 0.1 # filter_predictions
    _large_table_merge_distance: float = 0.6 # lta strategy settings
    _smallest_supported_text_height: float = 0.1 # generic strategy settings
```