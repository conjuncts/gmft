import copy

import pandas as pd


from gmft.algorithm.ditr_structure import (
    _clean_predictions,
    _determine_headers_and_projecting,
)
from gmft.core._dataclasses import non_defaults_only, with_config
from gmft.algorithm.dividers import (
    fill_using_true_partitions,
    get_good_between_dividers,
)
from gmft.core.io.serial.dicts import (
    _extract_effective,
    _extract_fctn_results,
    _extract_indices,
)
from gmft.core.legacy.fctn_results import LegacyFctnResults
from gmft.core.ml import _resolve_device
from gmft.core.ml.prediction import (
    TablePredictions,
    _empty_effective_predictions,
    _empty_indices_predictions,
)
from gmft.detectors.base import CroppedTable, RotatedCroppedTable
from gmft.impl.ditr.config import DITRFormatConfig
from gmft.formatters.base import FormattedTable, TableFormatter, _normalize_bbox
from gmft.formatters.histogram import HistogramFormattedTable
from gmft.pdf_bindings.base import BasePage


from gmft.algorithm.structure import (
    _non_maxima_suppression,
    _semantic_spanning_fill,
    _split_spanning_cells,
)
from gmft.table_visualization import plot_results_unwr, plot_shaded_boxes

import torch


class DITRFormattedTable(HistogramFormattedTable, LegacyFctnResults):
    """
    FormattedTable, as seen by a Table Transformer for dividers (dubbed DITR).
    See :class:`.DITRTableFormatter`.
    """

    id2label = {
        # 0: 'table',
        1: "column divider",  # table column',
        2: "row divider",  # table row',
        3: "top header",  # table column header',
        4: "projected",  # 'table projected row header',
        0: "spanning",  # 'table spanning cell',
        6: "no object",
    }
    label2id = {v: k for k, v in id2label.items()}

    config: DITRFormatConfig
    outliers: dict[str, bool]

    def __init__(
        self,
        cropped_table: CroppedTable,
        irvl_results: dict,
        fctn_results: dict,
        config: DITRFormatConfig = None,
    ):
        super(DITRFormattedTable, self).__init__(
            cropped_table, None, irvl_results, config=config
        )
        self.predictions = TablePredictions(
            bbox=fctn_results,
            effective=_empty_effective_predictions(),
            indices=_empty_indices_predictions(),
            status="unready",
        )

        if config is None:
            config = DITRFormatConfig()
        self.config = config
        self.outliers = None

    def df(self, recalculate=False, config_overrides: DITRFormatConfig = None):
        """
        Return the table as a pandas dataframe.
        :param recalculate: by default, the dataframe is cached. DEPRECATED: use recompute() instead.
        :param config_overrides: override the config settings for this call only
        """
        if recalculate != False:
            raise DeprecationWarning(
                "recalculate as a parameter in df() is deprecated; explicitly call recompute() instead. "
                "Will break in v0.6.0."
            )

        if self._df is None:
            self.recompute(config=config_overrides)
        return self._df

    def recompute(self, config: DITRFormatConfig = None):
        """
        Recompute the internal dataframe.
        """
        config = with_config(self.config, config)
        self._df = ditr_extract_to_df(self, config=config)
        return self._df

    def visualize(self, **kwargs):
        """
        Visualize the cropped table.
        """
        img = self.image()
        tbl_width = self.width  # adjust for rotations too
        tbl_height = self.height

        labels = []
        bboxes = []
        for x0, x1 in self.irvl_results["col_dividers"]:
            bboxes.append([x0, 0, x1, tbl_height])
            labels.append(1)
        for y0, y1 in self.irvl_results["row_dividers"]:
            bboxes.append([0, y0, tbl_width, y1])
            labels.append(2)
        for x0, y0, x1, y1 in self.predictions.effective["headers"]:
            bboxes.append([x0, y0, x1, y1])
            labels.append(3)
        for x0, y0, x1, y1 in self.predictions.effective["headers"]:
            bboxes.append([x0, y0, x1, y1])
            labels.append(4)
        for x0, y0, x1, y1 in self.predictions.effective["headers"]:
            bboxes.append([x0, y0, x1, y1])
            labels.append(5)
        return plot_shaded_boxes(img, labels=labels, boxes=bboxes, **kwargs)

    def to_dict(self):
        """
        Serialize self into dict
        """
        if self.angle != 0:
            parent = RotatedCroppedTable.to_dict(self)
        else:
            parent = CroppedTable.to_dict(self)
        optional = {}
        if self.predictions.status == "ready":
            optional["predictions.effective"] = self.predictions.effective
            optional["predictions.indices"] = self.predictions.indices
        return {
            **parent,
            **{
                "config": non_defaults_only(self.config),
                "outliers": self.outliers,
                "fctn_results": self.predictions.bbox,
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

        results = _extract_fctn_results(d)

        config = DITRFormatConfig(**d["config"])

        table = DITRFormattedTable(
            cropped_table,
            None,
            results,
            config=config,
        )
        table.recompute()
        table.outliers = d.get("outliers", None)
        table.predictions.indices = _extract_indices(d)
        table.predictions.effective = _extract_effective(d)
        if "predictions.effective" in d:
            table.predictions.status = "ready"
        return table


class DITRFormatter(TableFormatter):
    """
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.

    Using :meth:`extract`, a :class:`.FormattedTable` is produced, which can be exported to csv, df, etc.
    """

    def __init__(self, config: DITRFormatConfig = None):
        import transformers
        from transformers import AutoImageProcessor, TableTransformerForObjectDetection

        if config is None:
            config = DITRFormatConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)

        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(
            config.image_processor_path
        )
        # might need revision: "no_timm"
        self.structor = TableTransformerForObjectDetection.from_pretrained(
            config.formatter_path
        ).to(_resolve_device(config.torch_device))
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
    ) -> DITRFormattedTable:
        """
        Extract the data from the table.
        """

        config = with_config(self.config, config_overrides)

        image = table.image(dpi=dpi, padding=padding, margin=margin)  # (20, 20, 20, 20)
        padding = table._img_padding
        margin = table._img_margin

        scale_factor = dpi / 72
        encoding = self.image_processor(
            image,
            size={"shortest_edge": 800, "longest_edge": 1333},
            return_tensors="pt",
        ).to(_resolve_device(self.config.torch_device))
        with torch.no_grad():
            outputs = self.structor(**encoding)

        target_sizes = [image.size[::-1]]
        results = self.image_processor.post_process_object_detection(
            outputs,
            threshold=config.formatter_base_threshold,
            target_sizes=target_sizes,
        )[0]

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

        formatted_table = DITRFormattedTable(
            table,
            None,
            results,
            config=config,
        )
        formatted_table.recompute()
        return formatted_table


def ditr_extract_to_df(table: DITRFormattedTable, config: DITRFormatConfig = None):
    """
    Return the table as a pandas dataframe.
    The code is adapted from the gmft.algorithm.structure.extract_to_df()
    """

    if config is None:
        config = table.config

    outliers = {}  # store table-wide information about outliers or pecularities

    locations = _clean_predictions(table.predictions.bbox, config)
    row_dividers = locations.row_dividers
    col_dividers = locations.col_dividers
    row_divider_intervals = locations.row_divider_intervals
    col_divider_intervals = locations.col_divider_intervals
    top_headers = locations.top_headers
    projected = locations.projected
    spanning_cells = locations.spanning

    table.irvl_results = {
        "row_dividers": row_divider_intervals,
        "col_dividers": col_divider_intervals,
    }

    table.predictions.effective = {
        "rows": [],
        "columns": [],
        "headers": top_headers,
        "projecting": projected,
        "spanning": [span["bbox"] for span in spanning_cells],
    }

    # table_bounds = table.bbox # empirical_table_bbox(row_divider_boxes, col_divider_boxes)
    fixed_table_bounds = (0, 0, table.width, table.height)  # adjust for rotations too

    table_array = fill_using_true_partitions(
        table.text_positions(remove_table_offset=True),
        row_dividers=row_dividers,
        column_dividers=col_dividers,
        table_bounds=fixed_table_bounds,
    )

    # delete empty rows
    if config.remove_null_rows:
        empty_rows = [
            n
            for n in range(len(row_dividers) + 1)
            if all(x is None for x in table_array[n, :])
        ]
    else:
        empty_rows = []

    num_rows = len(row_dividers) + 1
    num_columns = len(col_dividers) + 1

    # Phase II: Rowspan and Colspan.

    # note that row intervals are not used to place text,
    # but rather for table structure recognition to determine which rows
    # are headers, projecting, spanning, etc.

    # need to add inverted to make sense of header_indices

    good_row_intervals = get_good_between_dividers(
        row_divider_intervals,
        fixed_table_bounds[1],
        fixed_table_bounds[3],
        add_inverted=True,
    )
    good_column_intervals = get_good_between_dividers(
        col_divider_intervals,
        fixed_table_bounds[0],
        fixed_table_bounds[2],
        add_inverted=True,
    )

    # find indices of key rows
    header_indices, projecting_indices = _determine_headers_and_projecting(
        good_row_intervals, top_headers, projected
    )

    if empty_rows:
        header_indices = [i for i in header_indices if i not in empty_rows]
        projecting_indices = [i for i in projecting_indices if i not in empty_rows]

    # semantic spanning fill
    indices_preds = {}
    if config.semantic_spanning_cells:
        # TODO probably not worth it to duplicate the code
        old_rows = [(None, y0, None, y1) for y0, y1 in good_row_intervals]
        old_columns = [(x0, None, x1, None) for x0, x1 in good_column_intervals]

        (
            sorted_hier_top_headers,
            sorted_monosemantic_top_headers,
            sorted_hier_left_headers,
        ) = _split_spanning_cells(
            spanning_cells, top_headers, old_rows, old_columns, header_indices
        )
        # since these are inherited from spanning cells, NMS is still necessary
        _non_maxima_suppression(
            sorted_hier_top_headers,
            overlap_threshold=config._nms_overlap_threshold_larger,
        )
        _non_maxima_suppression(
            sorted_monosemantic_top_headers,
            overlap_threshold=config._nms_overlap_threshold_larger,
        )
        _non_maxima_suppression(
            sorted_hier_left_headers,
            overlap_threshold=config._nms_overlap_threshold_larger,
        )
        hier_left_idxs = _semantic_spanning_fill(
            table_array,
            sorted_hier_top_headers,
            sorted_monosemantic_top_headers,
            sorted_hier_left_headers,
            header_indices=header_indices,
            config=config,
        )
        indices_preds["_hier_left"] = hier_left_idxs
    else:
        indices_preds["_hier_left"] = []  # for the user

    # technically these indices will be off by the number of header rows ;-;
    if config.enable_multi_header:
        indices_preds["_top_header"] = header_indices
    else:
        indices_preds["_top_header"] = [0] if header_indices else []

    # extract out the headers
    header_rows = table_array[header_indices]
    if config.enable_multi_header and len(header_rows) > 1:
        # Convert header rows to a list of tuples, where each tuple represents a column
        columns_tuples = list(zip(*header_rows))

        # Create a MultiIndex with these tuples
        column_headers = pd.MultiIndex.from_tuples(
            columns_tuples,
            names=[f"Header {len(header_rows) - i}" for i in range(len(header_rows))],
        )
        # Level is descending from len(header_rows) to 1

    else:
        # join by '\n' if there are multiple lines
        column_headers = [
            " \\n".join([row[i] for row in header_rows if row[i]])
            for i in range(num_columns)
        ]

    # note: header rows will be taken out
    table._df = pd.DataFrame(data=table_array, columns=column_headers)

    # a. mark as projecting/non-projecting
    if projecting_indices:
        is_projecting = [x in projecting_indices for x in range(num_rows)]
        # remove the header_indices
        # note that ditr._determine_headers_and_projecting
        # automatically makes is_projecting and header_indices mutually exclusive
        indices_preds["_projecting"] = [i for i, x in enumerate(is_projecting) if x]

    table.predictions.indices = indices_preds
    table.predictions.status = "ready"
    # b. drop the former header rows always
    table._df.drop(index=header_indices, inplace=True)

    # c. drop the empty rows
    table._df.drop(index=empty_rows, inplace=True)
    table._df.reset_index(drop=True, inplace=True)

    table.outliers = outliers
    return table._df
