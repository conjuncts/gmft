import statistics
from typing import TYPE_CHECKING
import numpy as np
from gmft.algorithm.dividers import (
    _ioa,
    fill_using_true_partitions,
)
from gmft.algorithm.structure import (
    _iob,
)
from gmft.core.ml.prediction import RawBboxPredictions
from gmft.detectors.base import CroppedTable
from gmft.formatters.base import FormattedTable
from gmft.impl.ditr.config import DITRFormatConfig
from gmft.impl.ditr.label import DITRLabel, DITRLocations
from gmft.impl.tatr.config import TATRFormatConfig

if TYPE_CHECKING:
    from gmft.formatters.ditr import DITRFormattedTable


def proportion_fctn_results(
    fctn_results: dict, config: DITRFormatConfig
) -> tuple[
    list[tuple[float, float, float, float, float]],
    list[tuple[float, float, float, float, float]],
    list[tuple[float, float, float, float]],
    list[tuple[float, float, float, float]],
    list[dict],
]:
    """
    Proportion the fctn_results into 5 categories:

    1. column dividers
    2. row dividers
    3. top headers
    4. projected rows
    5. spanning cells

    The first 2 are stored as tuples: (xmin, ymin, xmax, ymax, confidence).
    All are stored as direct tuples: (xmin, ymin, xmax, ymax),
    EXCEPT for the spanning cells, which is stored as a dict with keys 'bbox', 'confidence'.
    """
    # collated = []
    row_divider_boxes = []
    col_divider_boxes = []
    top_headers = []
    projected = []
    spanning_cells = []
    for confidence, label, bbox in zip(
        fctn_results["scores"], fctn_results["labels"], fctn_results["boxes"]
    ):
        if (
            confidence < config.cell_required_confidence[label]
        ):  # remove the unconfident
            continue
        if label == DITRLabel.row_divider:
            row_divider_boxes.append((*bbox, confidence))
        elif label == DITRLabel.column_divider:
            col_divider_boxes.append((*bbox, confidence))
        elif label == DITRLabel.top_header:
            top_headers.append(bbox)
        elif label == DITRLabel.projected:
            projected.append(bbox)
        elif label == DITRLabel.spanning:
            spanning_cells.append({"bbox": bbox, "confidence": confidence})
    return row_divider_boxes, col_divider_boxes, top_headers, projected, spanning_cells


def _determine_headers_and_projecting(
    row_intervals, sorted_headers, sorted_projecting, iob_threshold=0.7
):
    """
    Splits the sorted_horizontals into rows, headers, and projecting rows.
    Then, identifies a list of indices of headers and projecting rows.

    :param row_intervals: list of tuples, each tuple is a row interval (y0, y1)
    :param sorted_headers: list of bboxes (x0, y0, x1, y1) of headers
    :param sorted_projecting: list of bboxes (x0, y0, x1, y1) of projecting rows
    """

    # determine which rows overlap (> 0.9) with headers
    header_indices = []
    projecting_indices = []

    # iterate through pairs of row dividers
    # consider = [table_bounds[1]] + row_dividers + [table_bounds[3]]
    # for i in range(len(consider) - 1):
    # row_y_interval = (consider[i], consider[i+1])
    for i, row_y_interval in enumerate(row_intervals):
        # probably don't need to binary-ify, because usually the # of headers is 1
        for _, header_y0, _, header_y1 in sorted_headers:
            if _ioa(row_y_interval, (header_y0, header_y1)) > iob_threshold:
                header_indices.append(i)
        else:
            for _, proj_y0, _, proj_y1 in sorted_projecting:
                if _ioa(row_y_interval, (proj_y0, proj_y1)) > iob_threshold:
                    projecting_indices.append(i)
                    break
    return header_indices, projecting_indices


def _non_maxima_suppression_t(sorted_rows: list[tuple], overlap_threshold=0.1):
    """
    accepts (xmin, ymin, xmax, ymax, confidence)
    """
    num_removed = 0
    i = 1
    while i < len(sorted_rows):
        prev = sorted_rows[i - 1]
        cur = sorted_rows[i]
        if _iob(prev[:4], cur[:4]) > overlap_threshold:
            if prev[4] > cur[4]:
                sorted_rows.pop(i)
            else:
                sorted_rows.pop(i - 1)
            num_removed += 1
        else:
            i += 1
    return num_removed


def empirical_table_bbox(row_divider_boxes, col_divider_boxes):
    """
    We have access to the table bbox from the cropped table, but we can
    also estimate it from the dividers.

    I guess we could also take the max width/height of every divider.
    """
    average_x0 = (
        statistics.mean([box[0] for box in col_divider_boxes])
        if col_divider_boxes
        else -np.inf
    )
    average_x1 = (
        statistics.mean([box[2] for box in col_divider_boxes])
        if col_divider_boxes
        else np.inf
    )
    average_y0 = (
        statistics.mean([box[1] for box in row_divider_boxes])
        if row_divider_boxes
        else -np.inf
    )
    average_y1 = (
        statistics.mean([box[3] for box in row_divider_boxes])
        if row_divider_boxes
        else np.inf
    )
    return (average_x0, average_x1, average_y0, average_y1)


def _clean_predictions(
    results: RawBboxPredictions,
    config: DITRFormatConfig = None,
):
    row_divider_boxes, col_divider_boxes, top_headers, projected, spanning_cells = (
        proportion_fctn_results(results, config)
    )

    # Phase I: Separating lines

    # 2a. sort by ymean, xmean
    row_divider_boxes.sort(key=lambda box: (box[1] + box[3]) / 2)
    col_divider_boxes.sort(key=lambda box: (box[0] + box[3]) / 2)

    # apply nms
    _non_maxima_suppression_t(
        row_divider_boxes, overlap_threshold=config._nms_overlap_threshold
    )
    _non_maxima_suppression_t(
        col_divider_boxes, overlap_threshold=config._nms_overlap_threshold
    )

    row_dividers = [(y0 + y1) / 2 for x0, y0, x1, y1, _ in row_divider_boxes]
    col_dividers = [(x0 + x1) / 2 for x0, y0, x1, y1, _ in col_divider_boxes]

    row_divider_intervals = [(y0, y1) for _, y0, _, y1, _ in row_divider_boxes]
    col_divider_intervals = [(x0, x1) for x0, _, x1, _, _ in col_divider_boxes]

    return DITRLocations(
        row_dividers=row_dividers,
        col_dividers=col_dividers,
        row_divider_intervals=row_divider_intervals,
        col_divider_intervals=col_divider_intervals,
        top_headers=top_headers,
        projected=projected,
        spanning=spanning_cells,
    )

