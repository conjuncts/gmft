from typing import List
from gmft.algorithm.dividers import (
    _fill_using_true_partitions_include_endpoints,
    _to_table_bounds,
    fill_using_true_partitions,
    find_column_for_target,
    find_row_for_target,
)
from gmft.algorithm.partition_structure import _separate_horizontals, pairwise
from gmft.algorithm.structure import (
    _clean_tatr_predictions,
)
from gmft.core.ml.prediction import RawBboxPredictions
from gmft.core.schema import TableTextBbox
from gmft.formatters.base import FormattedTable
from gmft.impl.ditr.label import DITRLocations
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.reformat.schema import FormatState, Partitions
from gmft.reformat._calc.polaric import _table_to_words_df


def _ditr_locations_to_partitions(
    locations: DITRLocations,
    # table_bbox: tuple[float, float, float, float] = None,
    table_width: float,
    table_height: float,
) -> Partitions:
    # add table bbox as partitions

    return Partitions(
        # table_bbox=table_bbox,
        row_dividers=[0, *locations.row_dividers, table_height],
        col_dividers=[0, *locations.col_dividers, table_width],
        top_header_y=max(locations.top_headers, key=lambda x: x[3], default=0),
        left_header_x=0,
        projected=locations.projected,
        spanning=locations.spanning,
    )


def _tatr_predictions_to_partitions(
    tatr: RawBboxPredictions,
    config: TATRFormatConfig,
    table_width: float = None,
    table_height: float = None,
    word_height: float = 10,
) -> Partitions:
    """
    Converts TATR predictions to Partitions.
    """

    fixed = _clean_tatr_predictions(
        tatr, word_height=word_height, outliers={}, config=config
    )

    # simplest conversion from tatr bboxes to dividers:
    # take pairwise
    # TODO: consider the caveats of this algorithm.

    row_dividers = [0]
    col_dividers = [0]
    for prev, curr in pairwise(fixed["rows"]):
        # take average of the bottom of the previous and top of the current row
        row_dividers.append((prev["bbox"][3] + curr["bbox"][1]) / 2)
    row_dividers.append(table_height)

    for prev, curr in pairwise(fixed["columns"]):
        # take average of the right of the previous and left of the current column
        col_dividers.append((prev["bbox"][2] + curr["bbox"][0]) / 2)
    col_dividers.append(table_width)

    return Partitions(
        row_dividers=row_dividers,
        col_dividers=col_dividers,
        top_header_y=max([x["bbox"][3] for x in fixed["headers"]], default=0),
        left_header_x=0,
        projected=fixed["projecting"],
        spanning=fixed["spanning"],
    )


def partition_extract_to_state(
    locations: Partitions,
    *,
    table: FormattedTable,
) -> FormatState:
    """
    Return the table as a 2D numpy array with text.
    The code is adapted from ditr_extract_to_df().

    :param locations: Partitions object containing row and column dividers.
    :param table: FormattedTable object containing text positions and other metadata.
    :return: FormatState object
    """

    table_bbox = _to_table_bounds(locations.row_dividers, locations.col_dividers)

    row_dividers = locations.row_dividers
    col_dividers = locations.col_dividers

    projected = locations.projected

    # NOTE: removed setting table.irvl_results
    # NOTE: removed setting table.predictions.effective

    assert table_bbox == (0, 0, table.width, table.height), "Table bounds mismatch"

    table_array = _fill_using_true_partitions_include_endpoints(
        table.text_positions(remove_table_offset=True),
        row_dividers=row_dividers,
        column_dividers=col_dividers,
    )

    # delete empty rows
    empty_rows = [
        n for n in range(len(table_array)) if all(x is None for x in table_array[n])
    ]

    # find indices of key rows
    header_indices, projecting_indices = _separate_horizontals(
        row_dividers=row_dividers,
        top_header_y=locations.top_header_y,
        projected=projected,
    )

    if empty_rows:
        header_indices = [i for i in header_indices if i not in empty_rows]
        projecting_indices = [i for i in projecting_indices if i not in empty_rows]

    # TODO semantic spanning cells (left header) logic needs to be reinstated
    # TODO: top header logic needs to be reinstated

    return FormatState(
        words=_table_to_words_df(table),
        # table_array=table_array,
        header_rows=header_indices,
        projected_rows=projecting_indices,
        empty_rows=empty_rows,
        partitions=locations,
    )


def table_to_textbbox_list(
    ft: FormattedTable, row_dividers, col_dividers
) -> List[TableTextBbox]:
    # Step 1: Get the words as a list of dicts
    words = []
    for xmin, ymin, xmax, ymax, text in ft.text_positions(
        remove_table_offset=True, _split_hyphens=True
    ):
        x_center = (xmin + xmax) / 2
        y_center = (ymin + ymax) / 2

        # Find which bin the center falls into
        col_idx = find_column_for_target(col_dividers, x_center) - 1
        # then, it belongs to the xi-th column of the np array (no off by 1 error)

        row_idx = find_row_for_target(row_dividers, y_center) - 1

        words.append(
            {
                "text": text,
                "row_idx": row_idx,
                "col_idx": col_idx,
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
            }
        )

    return words
