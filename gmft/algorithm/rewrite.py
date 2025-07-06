
from gmft.algorithm.dividers import fill_using_true_partitions
from gmft.core.ml.prediction import Partitions, RawBboxPredictions
from gmft.formatters.base import FormattedTable
from gmft.impl.ditr.label import DITRLocations
from gmft.impl.tatr.config import TATRFormatConfig


def _ditr_locations_to_partitions(
    locations: DITRLocations,
    table_bbox: tuple[float, float, float, float] = None,
) -> Partitions:
    return Partitions(
        table_bbox=table_bbox,
        row_dividers=locations.row_dividers,
        col_dividers=locations.col_dividers,
        top_header_y=max(locations.top_headers, key=lambda x: x[3], default=0),
        left_header_x=0,
        projected=locations.projected,
        spanning=locations.spanning,
    )


def _tatr_predictions_to_partitions(
    tatr: RawBboxPredictions,
    table_bbox: tuple[float, float, float, float],
    config: TATRFormatConfig,
) -> Partitions:
    """
    Converts TATR predictions to Partitions.
    """



def partition_extract_to_arr(
    locations: Partitions,
    *,
    table: FormattedTable,
):
    """
    Return the table as a 2D numpy array with text.
    The code is adapted from ditr_extract_to_df().
    """

    outliers = {}  # store table-wide information about outliers or pecularities

    table_bbox = locations.table_bbox
    row_dividers = locations.row_dividers
    col_dividers = locations.col_dividers
    # row_divider_intervals = locations.row_divider_intervals
    # col_divider_intervals = locations.col_divider_intervals
    # top_headers = locations.top_headers

    top_headers = [(table_bbox[0], table_bbox[1], table_bbox[2], locations.top_header_y)]
    projected = locations.projecting
    spanning_cells = locations.spanning

    # table.irvl_results = {
    #     "row_dividers": row_divider_intervals,
    #     "col_dividers": col_divider_intervals,
    # }

    if table is not None:
        table.predictions.effective = {
            "rows": [],
            "columns": [],
            "headers": top_headers,
            "projecting": projected,
            "spanning": spanning_cells,
        }

    assert table_bbox == (0, 0, table.width, table.height), "Table bounds mismatch"

    table_array = fill_using_true_partitions(
        table.text_positions(remove_table_offset=True),
        row_dividers=row_dividers,
        column_dividers=col_dividers,
        table_bounds=table_bbox,
    )

    # delete empty rows
    # if config.remove_null_rows:
    #     empty_rows = [
    #         n
    #         for n in range(len(row_dividers) + 1)
    #         if all(x is None for x in table_array[n, :])
    #     ]
    # else:
    #     empty_rows = []

    num_rows = len(row_dividers) + 1
    num_columns = len(col_dividers) + 1

    # Phase II: Rowspan and Colspan.

    # note that row intervals are not used to place text,
    # but rather for table structure recognition to determine which rows
    # are headers, projecting, spanning, etc.

    # need to add inverted to make sense of header_indices

    # good_row_intervals = get_good_between_dividers(
    #     row_divider_intervals,
    #     fixed_table_bounds[1],
    #     fixed_table_bounds[3],
    #     add_inverted=True,
    # )
    # good_column_intervals = get_good_between_dividers(
    #     col_divider_intervals,
    #     fixed_table_bounds[0],
    #     fixed_table_bounds[2],
    #     add_inverted=True,
    # )

    # produce 


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
