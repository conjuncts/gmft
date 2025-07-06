from gmft.algorithm.dividers import _fill_using_true_partitions_include_endpoints, _to_table_bounds, fill_using_true_partitions
from gmft.algorithm.partition_structure import _separate_horizontals
from gmft.core.ml.prediction import RawBboxPredictions
from gmft.formatters.base import FormattedTable
from gmft.impl.ditr.label import DITRLocations
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.reformat.state import FormatState, Partitions


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

    table_bbox = _to_table_bounds(locations.row_dividers, locations.col_dividers)

    # row_dividers = locations.row_dividers[1:-1]
    # col_dividers = locations.col_dividers[1:-1]

    row_dividers = locations.row_dividers
    col_dividers = locations.col_dividers
    # row_divider_intervals = locations.row_divider_intervals
    # col_divider_intervals = locations.col_divider_intervals
    # top_headers = locations.top_headers

    # top_headers = [(table_bbox[0], table_bbox[1], table_bbox[2], locations.top_header_y)]
    projected = locations.projected
    # spanning_cells = locations.spanning

    # table.irvl_results = {
    #     "row_dividers": row_divider_intervals,
    #     "col_dividers": col_divider_intervals,
    # }

    # if table is not None:
    #     table.predictions.effective = {
    #         "rows": [],
    #         "columns": [],
    #         "headers": top_headers,
    #         "projecting": projected,
    #         "spanning": spanning_cells,
    #     }

    assert table_bbox == (0, 0, table.width, table.height), "Table bounds mismatch"

    table_array = _fill_using_true_partitions_include_endpoints(
        table.text_positions(remove_table_offset=True),
        row_dividers=row_dividers,
        column_dividers=col_dividers,
    )

    # delete empty rows
    empty_rows = [
        n
        for n in range(len(table_array))
        if all(x is None for x in table_array[n])
    ]

    # find indices of key rows
    header_indices, projecting_indices = _separate_horizontals(
        row_dividers=row_dividers, top_header_y=locations.top_header_y, projected=projected,
    )

    if empty_rows:
        header_indices = [i for i in header_indices if i not in empty_rows]
        projecting_indices = [i for i in projecting_indices if i not in empty_rows]

    # TODO semantic spanning cells (left header) logic needs to be reinstated

    # TODO: top header logic needs to be reinstated

    return FormatState(
        table_array=table_array,
        header_rows=header_indices,
        projected_rows=projecting_indices,
        empty_rows=empty_rows,
        partitions=locations
    )
