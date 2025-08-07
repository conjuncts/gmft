import copy
import dataclasses
from typing import Callable, List, Iterable, Iterator, Sequence, Tuple, TypeVar

from matplotlib import table
from gmft.algorithm.dividers import (
    _fill_using_true_partitions_include_endpoints,
    _symmetric_ioa,
    _to_table_bounds,
    fill_using_true_partitions,
    find_column_for_target,
    find_row_for_target,
    _ioa,
)
from gmft.algorithm.structure import (
    _clean_tatr_predictions,
    _find_leftmost_gt,
    _iob_for_rows,
    _nms_indices,
    _non_maxima_suppression,
    _symmetric_iob_for_columns,
    _symmetric_iob_for_rows,
)
from gmft.core.ml.prediction import BboxPrediction, RawBboxPredictions
from gmft.core.words_list import WordsList
from gmft.formatters.base import FormattedTable
from gmft.impl.ditr.label import DITRLocations
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.reformat.schema import (
    CellMerger,
    CellMergerType,
    SpanningPrediction,
    TableStructureWithArray,
    TableStructureWithWords,
    Partitions,
)


T = TypeVar("T")


def pairwise(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
    """
    Drop-in replacement for itertools.pairwise.

    pairwise('ABCDEFG') → AB BC CD DE EF FG
    """
    iterator = iter(iterable)
    a = next(iterator, None)

    for b in iterator:
        yield a, b
        a = b


def _separate_horizontals(
    *,
    row_dividers: list[float],
    top_header_y: float,
    projected,
    iob_threshold=0.7,
):
    """
    Separates the sorted_horizontals into rows, headers, and projecting rows.
    Then, identifies a list of indices of headers and projecting rows.

    Formerly called _determine_headers_and_projecting

    :param row_intervals: list of dividers, including endbounds
    :param top_header_y: y value which separates the top header from the rest of the table
    :param projected: list of bboxes (x0, y0, x1, y1) of projecting rows
    """

    # determine which rows overlap (> 0.9) with headers
    header_indices = []
    projecting_indices = []

    # iterate through pairs of row dividers
    for i, row_y_interval in enumerate(pairwise(row_dividers)):
        # Define a header to be one where >70% of row is in the header region
        if _ioa(row_y_interval, (0, top_header_y)) > iob_threshold:
            header_indices.append(i)
            continue

        # Define a projecting row to be one where >70% of row is in the projecting region
        if any(
            _ioa(row_y_interval, (proj_y0, proj_y1)) > iob_threshold
            for _, proj_y0, _, proj_y1 in projected
        ):
            projecting_indices.append(i)
            continue

    return header_indices, projecting_indices


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


def partition_extract_to_words_state(
    locations: Partitions,
    *,
    table: FormattedTable,
) -> TableStructureWithWords:
    """
    Return the table as a 2D numpy array with text.
    The code is adapted from ditr_extract_to_df().

    :param locations: Partitions object containing row and column dividers.
    :param table: FormattedTable object containing text positions and other metadata.
    :return: FormatState object
    """

    table_bbox = _to_table_bounds(locations.row_dividers, locations.col_dividers)

    # NOTE: removed setting table.irvl_results
    # NOTE: removed setting table.predictions.effective

    assert table_bbox == (0, 0, table.width, table.height), "Table bounds mismatch"

    wl = WordsList.from_table(table)
    words_struct = TableStructureWithWords(
        words=wl,
        locations=locations,
    )
    return words_struct


def fill_2d_array(
    words_struct: TableStructureWithWords,
) -> TableStructureWithArray:
    locations = words_struct.locations
    row_dividers = locations.row_dividers
    col_dividers = locations.col_dividers
    projected = locations.projected

    table_array = _fill_using_true_partitions_include_endpoints(
        words_struct.words.iter_words(),
        row_dividers=row_dividers,
        column_dividers=col_dividers,
    )

    # keep track of empty rows
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

    # here, the table array retains empty rows, but they are specially marked

    # TODO semantic spanning cells (left header) logic needs to be reinstated
    # TODO: top header logic needs to be reinstated

    array_struct = TableStructureWithArray(
        locations=locations,
        words=words_struct.words,
        table_array=table_array,
        header_rows=header_indices,
        projected_rows=projecting_indices,
        empty_rows=empty_rows,
        merges=[],
    )

    return array_struct


def _find_all_indices_for_interval(
    haystack: list[tuple[float, float]],
    needle: tuple[float, float],
    threshold=0,
    _ioa: Callable[[Tuple[float, float], Tuple[float, float]], float] = _ioa,
):
    """
    Given a needle [p, q], find all indices in haystack where _ioa exceeds threshold.
    Find all rows that intersect with the box.
    :param sorted_rows: list of bboxes, so list of tuples (xmin, ymin, xmax, ymax)
    :return list of indices of rows
    """
    rows = []
    ymin, ymax = needle
    # Equivalent to linear search through sorted_rows
    i = _find_leftmost_gt(haystack, ymin, lambda row: row[1])
    while i < len(haystack):
        row = haystack[i]
        iob_score = _ioa(needle, row)

        if iob_score > threshold:
            rows.append(i)
        # we may break early when the row is below the textbox
        # this assumes that row_min and row_max are roughly accurate
        if ymax < row[1]:
            break
        i += 1
    return rows


def _calculate_local_merges(
    spanning_cells: list[BboxPrediction],
    # sorted_headers_bboxes: list[tuple[float, float, float, float]],
    header_top_y: float,
    row_splits: list[float],
    col_splits: list[float],
    header_indices: list[int],
) -> list[CellMerger]:
    """
    Split spanning cells into 2 categories:
    a) those within column headers (and therefore likely represent info on hierarchical column headers). These reside on top
    b) those outside (likely represent hierarchical row headers). These reside on the left

    More specifically,
    require hierarchical column headers to span only 1 row, and hierarchical row headers to span only 1 column.

    :param spanning_cells: list of dictionaries, each with keys 'bbox', 'confidence', 'label'
    :param sorted_headers: list[tuple[float, float, float, float]] of bboxes (xmin, ymin, xmax, ymax)
    :param sorted_rows: list[tuple[float, float, float, float]] of bboxes (xmin, ymin, xmax, ymax)
    :param sorted_columns: list[tuple[float, float, float, float]] of bboxes (xmin, ymin, xmax, ymax)
    :param header_indices: list[int] of indices of rows that are headers
    :return spanning cells; hierarchical top headers, monosemantic top headers, hierarchical left headers

    See also: _split_spanning_cells
    """
    merges = []

    pairwise_rows = list(pairwise(row_splits))
    pairwise_cols = list(pairwise(col_splits))
    for pred in spanning_cells:
        cell = pred["bbox"]
        yavg = (cell[1] + cell[3]) / 2
        horiz_interval = (cell[0], cell[2])
        vert_interval = (cell[1], cell[3])
        if yavg < header_top_y:
            # good - it is located in the header
            all_valid_rows = _find_all_indices_for_interval(
                pairwise_rows,
                vert_interval,
                threshold=0.5,
                _ioa=_symmetric_ioa,
                # NOTE: tweaked to _symmetric_ioa and 0.5
            )

            all_valid_cols = _find_all_indices_for_interval(
                pairwise_cols,
                horiz_interval,
                threshold=0.5,
                _ioa=_symmetric_ioa,
            )

            all_valid_rows = [x for x in all_valid_rows if x in header_indices]
            # empty row/col is dealt with later

            if len(all_valid_rows) == 1:
                # a one-row header is a hierarchical top header
                dtype = CellMergerType.TOP_HIER

                # INSTR: aggregate text and repeat it throughout
                dtype |= CellMergerType.AGGREGATE | CellMergerType.REPEAT
            elif len(all_valid_cols) == 1:
                # a one-column header entirely within the top header
                # is not hierarchical, but rather monosemantic
                dtype = CellMergerType.TOP_NONHIER

                # INSTR: aggregate text, but only write to bottom-most cell
                dtype |= CellMergerType.AGGREGATE | CellMergerType.PUSH_FORWARD
            else:
                # unclassified
                dtype = CellMergerType.NONE
        else:
            # outside of top header - could be a left header
            all_valid_cols = _find_all_indices_for_interval(
                pairwise_cols,
                horiz_interval,
                threshold=0.5,
                _ioa=_symmetric_ioa,
                # wider threshold for left headers
                # we want them to solidly be in the spanning region
                # NOTE: tweaked to _symmetric_ioa and 0.5
                # TODO: different standard for 1st vs second
            )

            # bbox may be taller than each row, so use symmetric ioa
            all_valid_rows = _find_all_indices_for_interval(
                pairwise_rows, vert_interval, threshold=0.5, _ioa=_symmetric_ioa
            )

            if len(all_valid_cols) == 1:
                # a one-column header, not top-header, is likely left header
                dtype = CellMergerType.LEFT_HIER

                # INSTR: repeat text, make cell take value of previous
                dtype |= CellMergerType.REPEAT | CellMergerType.PUSH_FORWARD
            else:
                # unclassified. There may be a lot of these
                dtype = CellMergerType.NONE

        # empty row/col
        if not all_valid_rows:
            all_valid_rows = [None]
        if not all_valid_cols:
            all_valid_cols = [None]

        # in both cases, cell merger looks the same
        merger = CellMerger(
            row_min=all_valid_rows[0],
            col_min=all_valid_cols[0],
            row_max=all_valid_rows[-1],
            col_max=all_valid_cols[-1],
            dtype=dtype,
            debug=(all_valid_cols, all_valid_rows),
        )

        merges.append(merger)

    # sort hier_left by ascending y0
    # which is advantageous becauseit makes it closer to algo fill
    #     sorted_hier_left_headers.sort(key=lambda x: x["bbox"][1])

    return merges


def cut_spanning(array_struct: TableStructureWithArray) -> List[SpanningPrediction]:
    merges = _calculate_local_merges(
        spanning_cells=array_struct.locations.spanning,
        header_top_y=array_struct.locations.top_header_y,
        row_splits=array_struct.locations.row_dividers,
        col_splits=array_struct.locations.col_dividers,
        header_indices=array_struct.header_rows,
    )
    return [
        {**span, "merger": merger}
        for span, merger in zip(array_struct.locations.spanning, merges)
    ]


def generate_mergers(
    array_struct: TableStructureWithArray,
    *,
    _nms_overlap_threshold,
) -> TableStructureWithArray:
    """
    Merges left headers into the table array.

    :param array_struct: TableStructureWithArray object containing the table array and locations.
    :param _nms_overlap_threshold: Overlap threshold for non-maxima suppression.
    :return: Updated TableStructureWithArray with planned cell merges.
    """

    merges = cut_spanning(array_struct)

    # TODO: verify that we can turn spanning from tuple to BboxPrediction
    # TODO: make SpanMerge (CellMerger) that extends BboxPrediction
    # TODO: or make use of the CellMergerMetadata field

    # TODO: or actually, use a completely differnet approach. For each spanning
    # BboxPrediction, simply assign dtype and row/col indices (analogous to cut())
    # maybe call it cut_spanning()?

    # TODO: implement the 'algorithm' approach, which is as simple as
    # LEFT_HIER | REPEAT | PUSH_FORWARD

    # and that would be sufficient for _semantic_spanning_fill().
    sorted_top_hier = []
    sorted_top_nonhier = []
    sorted_left_hier: list[SpanningPrediction] = []
    uncls = []

    for merge in merges:
        if (merge["merger"].dtype & CellMergerType.TOP_HIER) != 0:
            sorted_top_hier.append(merge)
        elif (merge["merger"].dtype & CellMergerType.TOP_NONHIER) != 0:
            sorted_top_nonhier.append(merge)
        elif (merge["merger"].dtype & CellMergerType.LEFT_HIER) != 0:
            sorted_left_hier.append(merge)
        else:
            uncls.append(merge)

    # sort hier_left by ascending y0
    sorted_left_hier.sort(key=lambda x: x["bbox"][1])

    # do some NMS (deduplication)
    _non_maxima_suppression(sorted_top_hier, overlap_threshold=_nms_overlap_threshold)
    _non_maxima_suppression(
        sorted_top_nonhier,
        overlap_threshold=_nms_overlap_threshold,
    )
    _non_maxima_suppression(sorted_left_hier, overlap_threshold=_nms_overlap_threshold)

    # order matters - this is the order in which _semantic_spanning_fill originally acted
    array_struct = dataclasses.replace(
        array_struct,
        merges=sorted_left_hier + sorted_top_hier + sorted_top_nonhier,
    )

    return array_struct

    # the function _semantic_spanning_fill actually executes the merges.
    # postponed to reformat executor
    # hier_left_idxs = _semantic_spanning_fill(
    #     table_array,
    #     sorted_hier_top_headers,
    #     sorted_monosemantic_top_headers,
    #     sorted_hier_left_headers,
    #     header_indices=header_indices,
    #     config=config,
    # )
    # indices_preds["_hier_left"] = hier_left_idxs


def rect_iter(x1, y1, x2, y2, x_step=1, y_step=1, column_major=False):
    """
    Yields (x, y) coordinates within a 2D rectangle, inclusive of both (x1, y1) and (x2, y2),
    with configurable step direction and column/row major ordering.

    Args:
        x1, y1 -- Start coordinates (inclusive)
        x2, y2 -- End coordinates (inclusive)
        x_step, y_step -- Step sizes (can be negative)
        column_major -- If True, iterate columns first , otherwise rows first
    """

    # Handle inclusive range with direction
    if x_step > 0:
        x_range = range(x1, x2 + 1, x_step)
    else:
        x_range = range(x1, x2 - 1, x_step)

    if y_step > 0:
        y_range = range(y1, y2 + 1, y_step)
    else:
        y_range = range(y1, y2 - 1, y_step)

    if column_major:
        for x in x_range:
            for y in y_range:
                yield (x, y)
    else:
        for y in y_range:
            for x in x_range:
                yield (x, y)


def _execute_cell_merges(
    array_struct: TableStructureWithArray,
    # top_hier: list[SpanningPrediction],
    # top_nonhier: list[SpanningPrediction],
    # left_hier: list[SpanningPrediction],
    # header_indices: list[int],
    # config,
):
    """
    Fill the table array according to spanning cells.
    (Assumes that NMS has already been applied, and there are no conflicts)
    """

    table_array = copy.deepcopy(array_struct.table_array)

    merge_preds = array_struct.merges
    header_indices = array_struct.header_rows
    for merge_pred in merge_preds:
        merge = merge_pred["merger"]

        REPEAT = (merge.dtype & CellMergerType.REPEAT) != 0
        AGGREGATE = (merge.dtype & CellMergerType.AGGREGATE) != 0

        if merge.col_min is None or merge.row_min is None:
            # empty row or column, skip
            continue
        width = merge.col_max - merge.col_min + 1
        height = merge.row_max - merge.row_min + 1

        first_cell = (merge.row_min, merge.col_min)
        last_cell = (merge.row_max, merge.col_max)
        row_major = width > height

        push = 0
        if (merge.dtype & CellMergerType.PUSH_FORWARD) != 0:
            push = 1
        elif (merge.dtype & CellMergerType.PUSH_BACKWARD) != 0:
            push = -1

        # If aggregating, always aggregate LTR and top-bottom
        # TODO: this is biased towards LTR languages, ideally should be configurable
        # I guess could be solved with AGGREGATE_BACKWARD
        if AGGREGATE or push == 0:
            traverse_dir = 1
        else:
            traverse_dir = push

        # determine a traversal direction
        traversal = rect_iter(
            merge.row_min,
            merge.col_min,
            merge.row_max,
            merge.col_max,
            x_step=traverse_dir,
            y_step=traverse_dir,
            column_major=not row_major,
        )

        if REPEAT and AGGREGATE:
            # repeat and aggregate behavior:
            # aggregate the range, then repeat that to all cells

            # collect
            collector = ""
            traversal = list(traversal)  # need to reuse
            for i, j in traversal:
                cell_content = table_array[i][j]
                if cell_content:
                    collector += cell_content + " "

            # repeat
            for i, j in traversal:
                table_array[i][j] = collector.strip()

        elif push:
            # only defined when there is a single row or column
            if not (width == 1 or height == 1):
                continue

            if AGGREGATE:
                # aggregate the range, then push that to the first or last cell
                collector = ""
                for i, j in traversal:
                    cell_content = table_array[i][j]
                    if cell_content:
                        collector += cell_content + " "
                        table_array[i][j] = None
                if push == 1:
                    table_array[last_cell[0]][last_cell[1]] = collector.strip()
                else:
                    table_array[first_cell[0]][first_cell[1]] = collector.strip()

            elif REPEAT:
                # repeat the first cell's content to all cells in the traversal
                fill_value = table_array[first_cell[0]][first_cell[1]]
                if fill_value is not None:
                    for i, j in traversal:
                        cell_content = table_array[i][j]
                        if cell_content is None:
                            table_array[i][j] = fill_value
                        else:
                            fill_value = cell_content

    return dataclasses.replace(
        array_struct,
        table_array=table_array,
    )


def export_header(struct: TableStructureWithArray, *, enable_multi_header=False):
    """
    Exports headers for the table.
    """

    table_array = struct.table_array
    header_indices = struct.header_rows

    if not len(table_array):
        # empty; nothing to do
        return []
    num_columns = len(table_array[0])
    # extract out the headers
    header_rows = [table_array[i] for i in header_indices]
    # if config.enable_multi_header and len(header_rows) > 1:
    if enable_multi_header and len(header_rows) > 1:
        import pandas as pd

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

    return column_headers
    # note: header rows will be taken out
    # table._df = pd.DataFrame(data=table_array, columns=column_headers)


def _to_pandas(struct: TableStructureWithArray, column_headers):
    """
    Produce the pandas df
    """
    import pandas as pd

    header_indices = struct.header_rows
    table_array = struct.table_array

    # note: header rows will be taken out
    df = pd.DataFrame(data=table_array, columns=column_headers)

    # a. mark as projecting/non-projecting
    # if projecting_indices:
    #     is_projecting = [x in projecting_indices for x in range(num_rows)]
    #     # remove the header_indices
    #     # TODO this could be made O(n)
    #     is_projecting = [
    #         x for i, x in enumerate(is_projecting) if i not in header_indices
    #     ]
    #     indices_preds["_projecting"] = [i for i, x in enumerate(is_projecting) if x]

    # table.predictions.indices = indices_preds
    # table.predictions.status = "ready"

    # if projecting_indices:
    # insert at end

    # b. drop the former header rows always
    df.drop(index=header_indices, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def _to_polars(struct: TableStructureWithArray, column_headers):
    """
    Produce the polars df
    """

    import polars as pl

    header_indices = struct.header_rows
    table_array = [
        row for i, row in enumerate(struct.table_array) if i not in header_indices
    ]

    # note: header rows will be taken out
    df = pl.DataFrame(data=table_array, schema=[(h, pl.Utf8) for h in column_headers])
    return df

def _to_html(struct: TableStructureWithArray):
    """
    Produce the html version of the table
    """
    