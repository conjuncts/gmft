import copy
from dataclasses import dataclass, field
from typing import Union

from gmft.config._dataclasses import non_defaults_only, with_config
from gmft.detectors.base import CroppedTable, RotatedCroppedTable
from gmft.formatters.base import FormattedTable, TableFormatter, _normalize_bbox
from gmft.pdf_bindings.base import BasePage
import torch


from gmft.algorithm.structure import extract_to_df
from gmft.table_visualization import plot_results_unwr


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

    semantic_hierarchical_left_fill: Union[str, None] = "algorithm"
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


class TATRFormattedTable(FormattedTable):
    """
    FormattedTable, as seen by a Table Transformer (TATR).
    See :class:`.TATRTableFormatter`.
    """

    _POSSIBLE_ROWS = [
        "table row",
        "table spanning cell",
        "table projected row header",
    ]  # , 'table column header']
    _POSSIBLE_PROJECTING_ROWS = [
        "table projected row header"
    ]  # , 'table spanning cell']
    _POSSIBLE_COLUMN_HEADERS = ["table column header"]
    _POSSIBLE_COLUMNS = ["table column"]
    id2label = {
        0: "table",
        1: "table column",
        2: "table row",
        3: "table column header",
        4: "table projected row header",
        5: "table spanning cell",
        6: "no object",
    }
    label2id = {v: k for k, v in id2label.items()}

    config: TATRFormatConfig
    outliers: dict[str, bool]

    effective_rows: list[tuple]
    "Rows as seen by the image --> df algorithm, which may differ from what the table transformer sees."

    effective_columns: list[tuple]
    "Columns as seen by the image --> df algorithm, which may differ from what the table transformer sees."

    effective_headers: list[tuple]
    "Headers as seen by the image --> df algorithm."

    effective_projecting: list[tuple]
    "Projected rows as seen by the image --> df algorithm."

    effective_spanning: list[tuple]
    "Spanning cells as seen by the image --> df algorithm."

    _top_header_indices: list[int] = None
    _projecting_indices: list[int] = None
    _hier_left_indices: list[int] = None

    def __init__(
        self,
        cropped_table: CroppedTable,
        fctn_results: dict,
        config: TATRFormatConfig = None,
    ):
        super(TATRFormattedTable, self).__init__(cropped_table)
        self.fctn_results = fctn_results

        if config is None:
            config = TATRFormatConfig()
        self.config = config
        self.outliers = None

    def df(self, recalculate=False, config_overrides: TATRFormatConfig = None):
        """
        Return the table as a pandas dataframe.
        :param recalculate: by default, the dataframe is cached
        :param config_overrides: override the config settings for this call only
        """
        if (
            recalculate == False and config_overrides is None and self._df is not None
        ):  # cache
            return self._df

        config = with_config(self.config, config_overrides)

        return self.recompute(config=config)

    def recompute(self, config: TATRFormatConfig):
        """
        Recompute the internal dataframe.
        """
        self._df = extract_to_df(self, config=config)
        return self._df

    def visualize(
        self,
        filter=None,
        dpi=None,
        padding=None,
        margin=(10, 10, 10, 10),
        effective=False,
        return_img=True,
        **kwargs,
    ):
        """
        Visualize the table.

        :param filter: filter the labels to visualize. See TATRFormattedTable.id2label
        :param dpi: Sets the dpi. If none, then the dpi of the cached image is used.
        :param padding: padding around the table. If None, then the padding of the cached image is used.
        :param margin: margin around the table. If None, then the margin of the cached image is used.
        :param effective: if True, visualize the effective rows and columns, which may differ from the table transformer's output.
        :param return_img: if True, return the image. If False, the matplotlib figure is plotted.
        """
        if dpi is None:
            dpi = self._img_dpi
        if dpi is None:
            dpi = 72

        scale_by = dpi / 72

        if effective:
            if self._df is None:
                self._df = self.df()
            vis = (
                self.effective_rows
                + self.effective_columns
                + self.effective_headers
                + self.effective_projecting
                + self.effective_spanning
            )
            boxes = [x["bbox"] for x in vis]
            boxes = [(x * scale_by for x in bbox) for bbox in boxes]
            _to_visualize = {
                "scores": [x["confidence"] for x in vis],
                "labels": [self.label2id[x["label"]] for x in vis],
                "boxes": boxes,
            }
        else:
            # transform functionalized coordinates into image coordinates
            boxes = [
                (x * scale_by for x in bbox) for bbox in self.fctn_results["boxes"]
            ]

            _to_visualize = {
                "scores": self.fctn_results["scores"],
                "labels": self.fctn_results["labels"],
                "boxes": boxes,
            }

        # get needed scale factor and dpi
        img = self.image(dpi=dpi, padding=padding, margin=margin)
        true_margin = [x * (dpi / 72) for x in self._img_margin]
        return plot_results_unwr(
            img,
            _to_visualize["scores"],
            _to_visualize["labels"],
            _to_visualize["boxes"],
            TATRFormattedTable.id2label,
            filter=filter,
            padding=padding,
            margin=true_margin,
            return_img=return_img,
            **kwargs,
        )

    def to_dict(self):
        """
        Serialize self into dict
        """
        if self.angle != 0:
            parent = RotatedCroppedTable.to_dict(self)
        else:
            parent = CroppedTable.to_dict(self)
        optional = {}
        if self._projecting_indices is not None:
            optional["_projecting_indices"] = self._projecting_indices
        if self._hier_left_indices is not None:
            optional["_hier_left_indices"] = self._hier_left_indices
        if self._top_header_indices is not None:
            optional["_top_header_indices"] = self._top_header_indices
        return {
            **parent,
            **{
                "config": non_defaults_only(self.config),
                "outliers": self.outliers,
                "fctn_results": self.fctn_results,
            },
            **optional,
        }

    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize from dict.
        A page is required partly because of memory management, since having this open a page may cause memory issues.
        """
        d = copy.deepcopy(d)  # don't modify the original dict
        cropped_table = CroppedTable.from_dict(d, page)

        if "fctn_results" not in d:
            raise ValueError(
                "fctn_results not found in dict -- dict may be a CroppedTable but not a TATRFormattedTable."
            )

        config = TATRFormatConfig(**d["config"])

        results = d["fctn_results"]  # fix shallow copy issue
        if (
            "fctn_scale_factor" in d
            or "scale_factor" in d
            or "fctn_padding" in d
            or "padding" in d
        ):
            # deprecated: this is for backwards compatibility
            scale_factor = d.get("fctn_scale_factor", d.get("scale_factor", 1))
            padding = d.get("fctn_padding", d.get("padding", (0, 0)))
            padding = tuple(padding)

            # normalize results here
            for i, bbox in enumerate(results["boxes"]):
                results["boxes"][i] = _normalize_bbox(
                    bbox, used_scale_factor=scale_factor, used_padding=padding
                )

        table = TATRFormattedTable(
            cropped_table,
            results,
            config=config,
        )
        table.outliers = d.get("outliers", None)
        return table


class TATRFormatter(TableFormatter):
    """
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.

    Using :meth:`extract`, a :class:`.FormattedTable` is produced, which can be exported to csv, df, etc.
    """

    def __init__(self, config: TATRFormatConfig = None):
        import transformers
        from transformers import AutoImageProcessor, TableTransformerForObjectDetection

        if config is None:
            config = TATRFormatConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)

        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(
            config.image_processor_path
        )
        revision = "no_timm" if config.no_timm else None
        self.structor = TableTransformerForObjectDetection.from_pretrained(
            config.formatter_path, revision=revision
        ).to(config.torch_device)
        self.config = config
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)

    def extract(
        self,
        table: CroppedTable,
        dpi=144,
        padding="auto",
        margin=None,
        config_overrides=None,
    ) -> TATRFormattedTable:
        """
        Extract the data from the table.
        """

        config = with_config(self.config, config_overrides)

        image = table.image(dpi=dpi, padding=padding, margin=margin)  # (20, 20, 20, 20)
        padding = table._img_padding
        margin = table._img_margin

        scale_factor = dpi / 72
        encoding = self.image_processor(image, return_tensors="pt").to(
            self.config.torch_device
        )
        with torch.no_grad():
            outputs = self.structor(**encoding)

        target_sizes = [image.size[::-1]]
        # threshold = 0.3
        # note that a LOW threshold is good because the model is overzealous in
        # but since we find the highest-intersecting row, same-row elements still tend to stay together
        # this is better than having a high threshold, because if we have fewer rows than expected, we merge cells
        # losing information
        results = self.image_processor.post_process_object_detection(
            outputs,
            threshold=config.formatter_base_threshold,
            target_sizes=target_sizes,
        )[0]

        # create a new FormattedTable instance with the cropped table and the dataframe

        # return formatted_table
        results = {k: v.tolist() for k, v in results.items()}

        # normalize results w.r.t. padding and scale factor
        for i, bbox in enumerate(results["boxes"]):
            results["boxes"][i] = _normalize_bbox(
                bbox,
                used_scale_factor=scale_factor,
                used_padding=padding,
                used_margin=margin,
            )

        formatted_table = TATRFormattedTable(
            table,
            results,
            config=config,
        )
        return formatted_table


# legacy aliases
TATRTableFormatter = TATRFormatter
