
from __future__ import annotations # 3.7

import bisect
from typing import Generator
import numpy as np
import pandas as pd
from gmft.common import Rect
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gmft.table_function import TATRFormatConfig, TATRFormattedTable


def _iob(bbox1: tuple[float, float, float, float], bbox2: tuple[float, float, float, float]):
    """
    Compute the intersection area over box area, for bbox1.
    """
    intersection = Rect(bbox1).intersect(bbox2)
    
    bbox1_area = Rect(bbox1).area
    if bbox1_area > 0:
        return intersection.area / bbox1_area
    
    return 0

def _iob_for_rows(bbox1: tuple[float, float, float, float], bbox2: tuple[float, float, float, float]):
    """
    Modification of iob but for rows: pretend that the bboxes are infinitely wide. For bbox1.
    """
    a0, a1 = bbox1[1], bbox1[3]
    b0, b1 = bbox2[1], bbox2[3]
    
    intersect0, intersect1 = max(a0, b0), min(a1, b1)
    intersect_area = max(0, intersect1 - intersect0)
    
    return intersect_area / (a1 - a0)

def _iob_for_columns(bbox1: tuple[float, float, float, float], bbox2: tuple[float, float, float, float]):
    """
    Modification of iob but for columns: pretend that the bboxes are infinitely tall. For bbox1.
    """
    a0, a1 = bbox1[0], bbox1[2]
    b0, b1 = bbox2[0], bbox2[2]
    
    intersect0, intersect1 = max(a0, b0), min(a1, b1)
    intersect_area = max(0, intersect1 - intersect0)
    
    return intersect_area / (a1 - a0)

def _symmetric_iob(bbox1, bbox2):
    """
    Compute the intersection area over box area, for min of bbox1 and bbox2
    """
    intersection = Rect(bbox1).intersect(bbox2)
    
    bbox1_area = Rect(bbox1).area
    bbox2_area = Rect(bbox2).area
    if bbox1_area > 0 and bbox2_area > 0:
        return intersection.area / min(bbox1_area, bbox2_area)
    
    return 0

def _symmetric_iob_for_rows(bbox1, bbox2):
    """
    Modification of iob but for rows: pretend that the bboxes are infinitely wide. For min of bbox1 and bbox2.
    """
    a0, a1 = bbox1[1], bbox1[3]
    b0, b1 = bbox2[1], bbox2[3]
    
    intersect0, intersect1 = max(a0, b0), min(a1, b1)
    intersect_area = max(0, intersect1 - intersect0)
    
    return intersect_area / min(a1 - a0, b1 - b0)

def _find_rightmost_le(sorted_list, value, key_func):
    """Find rightmost value less than or equal to value
    Therefore, finds the rightmost box where box_min <= y1
    """
    i = bisect.bisect_right(sorted_list, value, key=key_func)
    if i:
        return i-1
    # raise ValueError
    return None

def _find_leftmost_gt(sorted_list, value, key_func):
    """Find leftmost value greater than value
    Therefore, finds the leftmost box where box_max > y_min
    
    In other words, the first row where the row might intersect y_min, even a little bit
    """
    i = bisect.bisect_left(sorted_list, value, key=key_func)
    # if i < len(sorted_list):
    return i
    # return None

def _predict_word_height(table):
    """
    Get the predicted height of standard text in the table.
    """
    # get the distribution of word heights, rounded to the nearest tenth
    word_heights = []
    for xmin, ymin, xmax, ymax, text in table.text_positions(remove_table_offset=True):
        # word_heights.append(round(ymax - ymin, 1))
        height = ymax - ymin
        if height > 0.1:
            word_heights.append(ymax - ymin)
    
    # get the mode
    # from collections import Counter
    # word_heights = Counter(word_heights)
    
    # # set the mode to be the row height
    # # making the row less than text's height will mean that no cells are merged
    # # but subscripts may be difficult
    # row_height = 0.95 * max(word_heights, key=word_heights.get)
    
    # actually no - use the median
    row_height = 0.95 * np.median(word_heights)
    return row_height

def _widen_and_even_out_rows(sorted_rows, sorted_headers):
    # widen the rows to the full width of the table
    leftmost = min([x['bbox'][0] for x in sorted_rows])
    rightmost = max([x['bbox'][2] for x in sorted_rows])
    for row in sorted_rows:
        row['bbox'][0] = leftmost
        row['bbox'][2] = rightmost
    for header in sorted_headers:
        header['bbox'][0] = leftmost
        header['bbox'][2] = rightmost


def _fill_in_gaps(sorted_rows, gap_height, leave_gap=0.4):
    # fill in gaps in the rows
    margin = leave_gap * gap_height
    
    i = 1
    while i < len(sorted_rows):
        prev = sorted_rows[i-1]
        cur = sorted_rows[i]
        if cur['bbox'][1] - prev['bbox'][3] > gap_height:
            # fill in the gap
            sorted_rows.insert(i, {'confidence': 1, 'label': 'table row', 'bbox': 
                                   [prev['bbox'][0], prev['bbox'][3] + margin, prev['bbox'][2], cur['bbox'][1] - margin]})
        i += 1
    

def _non_maxima_suppression(sorted_rows, overlap_threshold=0.1):
    """
    From the TATR authors' inference.py:
    If a lower-confidence object overlaps more than 5% of its area
    with a higher-confidence object, remove the lower-confidence object.
    """
    num_removed = 0
    i = 1
    while i < len(sorted_rows):
        prev = sorted_rows[i-1]
        cur = sorted_rows[i]
        if _iob(prev['bbox'], cur['bbox']) > overlap_threshold:
            if prev['confidence'] > cur['confidence']:
                sorted_rows.pop(i)
            else:
                sorted_rows.pop(i-1)
            num_removed += 1
        else:
            i += 1
    return num_removed
    

def _guess_row_bboxes_for_large_tables(table: TATRFormattedTable, config: TATRFormatConfig, sorted_rows, sorted_headers, known_means=None, known_height=None):
    if known_height:
        word_height = known_height
    else:
        # get the distribution of word heights, rounded to the nearest tenth
        if config.verbosity >= 1:
            print("Invoking large table row guess! set TATRFormatConfig.force_large_table_assumption to False to disable this.")        
        word_height = _predict_word_height(table)
    
    if not sorted_rows:
        return []
    # construct bbox for each row
    leftmost = min([x['bbox'][0] for x in sorted_rows])
    rightmost = max([x['bbox'][2] for x in sorted_rows])
    
    table_ymax = sorted_rows[-1]['bbox'][3]
    # we need to find the number of rows that can fit in the table
    
    new_rows = []

    # preserve existing rows inside the header, but otherwise start construction
    if sorted_headers:
        # is header-like
        while sorted_rows:
            row = sorted_rows[0]['bbox']
            if any(_iob_for_rows(row, header['bbox']) > 0.5 for header in sorted_headers):
                new_rows.append(sorted_rows.pop(0))
            else:
                break
        if not sorted_rows:
            # all rows are headers
            return new_rows
    y = sorted_rows[0]['bbox'][1]
        

    # fail-safe: if it predicts a very large table, raise
    est_num_rows = (table_ymax - y) / word_height
    if est_num_rows > config.large_table_maximum_rows:
        if config.verbosity >= 1:
            print(f"Estimated number of rows {est_num_rows} is too large")
        table.outliers['excessive rows'] = max(table.outliers.get('excessive rows', 0), est_num_rows)
        word_height = (table_ymax - y) / 100
    
    if known_means:
        # print(known_means)
        # construct rows, trying to center the rows on the known means
        starting_y = y
        prev_height = None
        for i, mean in enumerate(known_means):
            if mean < starting_y:
                # do not observe the header
                continue
            y = mean - word_height / 2
            # do NOT construct mini row if there is a gap
            # if prev_height is not None and y < prev_height:
                # new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, prev_height, rightmost, y]})
            new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, y, rightmost, y + word_height]})
            prev_height = y + word_height
            
    else:
        # this is reminiscent of the proof that the rationals are dense in the reals
        while y < table_ymax:
            new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, y, rightmost, y + word_height]})
            y += word_height
    # 2a. sort by ymax, just in case
    new_rows.sort(key=lambda x: x['bbox'][3])
    return new_rows
    # return col_headers 

def _split_sorted_horizontals(sorted_horizontals):
    sorted_rows = []
    sorted_headers = []
    sorted_projecting = []
    for x in sorted_horizontals:
        label = x['label']
        if label in ['table row']:
            sorted_rows.append(x)
        elif label in ['table column header', 'table row header']:
            sorted_headers.append(x)
        elif label in ['table projected row header']:
            sorted_projecting.append(x)
        elif label in ['table']:
            pass
        else:
            raise AssertionError(f"Unknown label {label}")
    return sorted_rows, sorted_headers, sorted_projecting

    

def _determine_headers_and_projecting(sorted_rows, sorted_headers, sorted_projecting):
    """
    Splits the sorted_horizontals into rows, headers, and projecting rows. 
    Then, identifies a list of indices of headers and projecting rows.
    """
    
    # determine which rows overlap (> 0.9) with headers
    header_indices = []
    projecting_indices = []
    
    if sorted_rows and sorted_headers:
        first_row = sorted_rows[0]
        first_header = sorted_headers[0]
        if first_row['bbox'][1] - 1 > first_header['bbox'][3]:
            # if the first row is below the first header, add the header as a row
            print("The header is not included as a row. Consider adding it back as a row.")
    
    for i, row in enumerate(sorted_rows):
        # TODO binary-ify
        if any(_iob(row['bbox'], header['bbox']) > 0.7 for header in sorted_headers):
            header_indices.append(i)
        if any(_iob(row['bbox'], proj['bbox']) > 0.7 for proj in sorted_projecting):
            projecting_indices.append(i)
    if not header_indices:
        # loosen the threshold
        for i, row in enumerate(sorted_rows):
            if any(_iob(row['bbox'], header['bbox']) > 0.5 for header in sorted_headers):
                header_indices.append(i)
    return header_indices, projecting_indices

def _find_all_rows_for_box(sorted_rows, bbox, threshold=0, _iob=_iob_for_rows):
    """
    Find all rows that intersect with the box.
    :return list of indices of rows
    """
    rows = []
    _, ymin, _, ymax = bbox
    # linsearch
    # for i, row in enumerate(sorted_rows):
    i = _find_leftmost_gt(sorted_rows, ymin, lambda row: row['bbox'][3])
    while i < len(sorted_rows):
        row = sorted_rows[i]
        iob_score = _iob(bbox, row['bbox'])
        if iob_score > threshold:
            rows.append(i)
        # we may break early when the row is below the textbox
        # this assumes that row_min and row_max are roughly 
        if ymax < row['bbox'][1]: # ymax < row_min
            break
        i += 1
    return rows

def _find_all_columns_for_box(sorted_columns, bbox, threshold=0, _iob=_iob_for_columns):
    """
    Find all columns that intersect with the box.
    """
    columns = []
    xmin, _, xmax, _ = bbox
    # linsearch
    # for i, row in enumerate(sorted_columns):
    i = _find_leftmost_gt(sorted_columns, xmin, lambda column: column['bbox'][2])
    while i < len(sorted_columns):
        column = sorted_columns[i]
        iob_score = _iob(bbox, column['bbox'])
        if iob_score > threshold:
            columns.append(i)
        if xmax < column['bbox'][0]: # xmax < column_min
            break
        i += 1
    return columns

def _find_best_row_for_text(sorted_rows, textbox):
    row_num = None
    row_max_iob = 0
    
    _, ymin, _, ymax = textbox
    
    # with binary search, we can only look at filtered subsets
    # get the first row that may intersect the textbox, even a little bit
    # so the first such row_ymax > ymin
    i = _find_leftmost_gt(sorted_rows, ymin, lambda row: row['bbox'][3])
    while i < len(sorted_rows):
        row = sorted_rows[i]
        iob_score = _iob(textbox, row['bbox'])
        if iob_score > row_max_iob:
            row_max_iob = iob_score
            row_num = i
        # we may break early when the row is below the textbox
        # this assumes that row_min and row_max are roughly 
        if ymax < row['bbox'][1]: # ymax < row_min
            break
        i += 1
    return row_num, row_max_iob

def _find_best_column_for_text(sorted_columns, textbox):
    column_num = None
    column_max_iob = 0
    xmin, _, xmax, _ = textbox
    # linsearch
    # for i, row in enumerate(sorted_columns):
    i = _find_leftmost_gt(sorted_columns, xmin, lambda column: column['bbox'][2])
    while i < len(sorted_columns):
        column = sorted_columns[i]
        iob_score = _iob(textbox, column['bbox'])
        if iob_score > column_max_iob:
            column_max_iob = iob_score
            column_num = i
        if xmax < column['bbox'][0]: # xmax < column_min
            break
        i += 1
    return column_num, column_max_iob


def _split_spanning_cells(spanning_cells, sorted_headers, sorted_rows, sorted_columns,
                          calculate_semantic_column_headers=False,
                          calculate_semantic_row_headers=True):
    """
    Split spanning cells into 2 categories: 
    a) those within column headers (and therefore likely represent info on hierarchical column headers). These reside on top
    b) those outside (likely represent hierarchical row headers). These reside on the left
    
    More specifically, 
    require hierarchical column headers to span only 1 row, and hierarchical row headers to span only 1 column.
    """
    sorted_spanning_top = []
    sorted_spanning_left = []
    for x in spanning_cells:
        if any(_iob(x['bbox'], header['bbox']) > 0.5 for header in sorted_headers):
            # good - it is located in the header
            if calculate_semantic_column_headers:
                all_valid_rows = _find_all_rows_for_box(sorted_rows, x['bbox'], threshold=0.2)
                
                # further require that it spans only 1 row
                if len(all_valid_rows) == 1:
                    row_idx = all_valid_rows[0]
                    col_indices = _find_all_columns_for_box(sorted_columns, x['bbox'], threshold=0.2, _iob=_iob_for_columns)
                    sorted_spanning_top.append((x, row_idx, col_indices))
            else:
                sorted_spanning_top.append((x, None, None))
        else:
            if calculate_semantic_row_headers:
                all_valid_cols = _find_all_columns_for_box(sorted_columns, x['bbox'], threshold=0.2)
                
                # further require that it spans only 1 column
                if len(all_valid_cols) == 1:
                    col_idx = all_valid_cols[0]
                    row_indices = _find_all_rows_for_box(sorted_rows, x['bbox'], threshold=0.2, _iob=_iob_for_rows)
                    sorted_spanning_left.append((x, col_idx, row_indices))
            else:
                sorted_spanning_left.append((x, None, None))
    
    # get the columns in which the left spanning cells reside
    left_spanning_indices = []
    rightmost_span = max([x['bbox'][2] for x in sorted_spanning_left])
    for i, col in enumerate(sorted_columns):
        if any(_iob(col['bbox'], span['bbox']) > 0.5 for span in sorted_spanning_left):
            left_spanning_indices.append(i)
        if col['bbox'][0] > rightmost_span: # break early if we surpass the rightmost span
            break

def _fill_using_partitions(text_positions: Generator[tuple[float, float, float, float, str], None, None], 
                          config: TATRFormatConfig, 
                          sorted_rows: list[dict], sorted_columns: list[dict], 
                          outliers: dict[str, bool], 
                        #   large_table_guess: bool, 
                          row_means: list[list[float]]):
    """
    Given estimated positions of rows, columns, headers and text positions,
    fills the table array.
    """

    num_rows = len(sorted_rows)
    num_columns = len(sorted_columns)
    table_array = np.empty([num_rows, num_columns], dtype="object")

    for xmin, ymin, xmax, ymax, text in text_positions:
        
        textbox = (xmin, ymin, xmax, ymax)

        # 5. let row_num be row with max iob
        row_num, row_max_iob = _find_best_row_for_text(sorted_rows, textbox)
        
        # 6. determine if is header
            
        if row_num is None:
            # if we ever do not record a value, something awry happened
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
        
        # 6. let column_num be column with max iob
        column_num, column_max_iob = _find_best_column_for_text(sorted_columns, textbox)
        
        # 7. check if it's a header
        # if possible_header:
        #     column_headers.setdefault(column_num, []).append(text)
        #     continue
        
        # we may now obtain row and column
        # if row_num is None:
            # continue
        row = sorted_rows[row_num]
        if column_num is None:
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
        column = sorted_columns[column_num]
        
        
        # 8. get the putative cell. check if it's a special cell
        
        # otherwise, we have a regular cell
        cell = Rect(row['bbox']).intersect(column['bbox'])
        
        # get iob: how much of the text is in the cell
        score = _iob(textbox, cell)
        
        if score < config.iob_reject_threshold: # poor match, like if score < 0.05
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
        
        # the "non-corner assumption" is that if the textbox has been clipped, it was clipped by
        # an edge and not a corner. For instance, demo|nstration is a clipped text, 
        # but "̵d̵e̵m̵'onstration" ("dem" is clipped by a corner) is invalid.
        
        # We may assume this because the row/column should stretch to the ends of the table
        # we can easily check this by seeing if row_max_iob and col_max_iob are independent
        
        # If this is not true, then it is not true in general that the best cell (most overlap)
        # is given by the intersection of the best row and the best column.
        
        # TODO calculate this directly from the score bbox and text bbox
        
        score_norm_deviation = abs(row_max_iob * column_max_iob - score) / score
        if score_norm_deviation > config.corner_clip_outlier_threshold:
            outliers['corner clip'] = True
        
        if score < config.iob_warn_threshold: # If <0.5 is the best, warn but proceed.
            outliers['lowest iob'] = min(outliers.get('lowest iob', 1), score)
        
        # update the table array, and join with ' ' if exists
        if row_means is not None:
            row_median = (ymax + ymin) / 2
            row_means[row_num].append(row_median)
            
        
        if table_array[row_num, column_num] is not None:
            table_array[row_num, column_num] += ' ' + text
        else:
            table_array[row_num, column_num] = text
    
    return table_array


def extract_to_df(table: TATRFormattedTable, config: TATRFormatConfig=None):
    """
    Return the table as a pandas dataframe.
    The code is adapted from the TATR authors' inference.py, with a few tweaks.
    """
    
    if config is None:
        config = table.config
    
    outliers = {} # store table-wide information about outliers or pecularities
    
    results = table.fctn_results

    # 1. collate identified boxes
    boxes = []
    for a, b, c in zip(results["scores"], results["labels"], results["boxes"]):
        bbox = c # .tolist()
        if a >= config.cell_required_confidence[b]:
            boxes.append({'confidence': a, 'label': table.id2label[b], 'bbox': bbox})
    
    # for cl, lbl_id, (xmin, ymin, xmax, ymax) in boxes:
    
    sorted_horizontals = []
    sorted_columns = []
    spanning_cells = []
    for box in boxes:
        label = box['label']
        if label == 'table spanning cell':
            spanning_cells.append(box)
        elif label in table._POSSIBLE_COLUMN_HEADERS or label in table._POSSIBLE_ROWS:
            sorted_horizontals.append(box)
        elif label in table._POSSIBLE_COLUMNS:
            sorted_columns.append(box)
    # 2a. sort by ymax
    sorted_horizontals.sort(key=lambda x: x['bbox'][3])
    # 2b. sort by xmax
    sorted_columns.sort(key=lambda x: x['bbox'][2])
    
    # print(len(sorted_rows), len(sorted_columns))
    if not sorted_horizontals or not sorted_columns:
        raise ValueError("No rows or columns detected")

    
    # 3. deduplicate, because tatr places a 2 bboxes for header (it counts as a header and a row)
    # only check consecutive rows/columns
    # i = 1
    # prev = sorted_horizontals[0]
    # while i < len(sorted_horizontals):
    #     cur = sorted_horizontals[i]
    #     if _symmetric_iob(prev['bbox'], cur['bbox']) > config.deduplication_iob_threshold:
    #         # pop the one that is a row
    #         # print("popping something")
    #         cur_priority = _priority_row(cur['label'])
    #         prev_priority = _priority_row(prev['label'])
    #         if cur_priority <= prev_priority:
    #             # pop cur
    #             sorted_horizontals.pop(i)
    #         elif cur_priority > prev_priority:
    #             sorted_horizontals.pop(i-1)
    #             prev = cur
    #     else:
    #         prev = cur
    #         i += 1
    sorted_rows, sorted_headers, sorted_projecting = _split_sorted_horizontals(sorted_horizontals)
    
    _non_maxima_suppression(sorted_projecting)
    # non-maxima suppression
    num_removed = _non_maxima_suppression(sorted_rows)
    if num_removed > 0 and config.verbosity >= 2:
        print(f"Removed {num_removed} overlapping rows")
    
    _widen_and_even_out_rows(sorted_rows, sorted_headers)
    
    word_height = _predict_word_height(table)
    _fill_in_gaps(sorted_rows, word_height)
    
    # 4a. calculate total row overlap. If higher than a threshold, invoke the large table assumption
    # also count headers
    table_area = table.rect.width * table.rect.height # * scale_factor ** 2
    total_row_area = 0
    for row in sorted_rows:
        total_row_area += (row['bbox'][2] - row['bbox'][0]) * (row['bbox'][3] - row['bbox'][1])

    # large table guess
    if config.force_large_table_assumption is None:
        large_table_guess = False
        if num_removed >= config.large_table_if_n_rows_removed:
            large_table_guess = True
        elif total_row_area > (1 + config.large_table_row_overlap_threshold) * table_area \
                and len(sorted_rows) > config.large_table_threshold:
            large_table_guess = True
            
    else:
        large_table_guess = config.force_large_table_assumption
    
    if large_table_guess:
        
        
        sorted_rows = _guess_row_bboxes_for_large_tables(table, config, sorted_rows, sorted_headers, known_height=word_height)
        left_corner = sorted_rows[0]['bbox']
        right_corner = sorted_rows[-1]['bbox']
        # (ymax - ymin) * (xmax - xmin)
        total_row_area = (right_corner[3] - left_corner[1]) * (right_corner[2] - left_corner[0])
        
        # outline: 
        # 1. allot each of the text into its row, which we can actually calculate using
        # (text-ymean / table_height) * num_rows is the index
        # 2. --> this estimate usually does not merge, but it does _split_
        # 2. for each row, calculate the mean of the y-values
        # 3. purge empty rows
        # 4. get a good estimate of the true row height by getting the (median) difference of means between rows
        # 5. (use a centering method (ie. mean, median, etc.) to get the row height, with robustness to split rows)
        # 6. re-estimate the rows
        bins = [[] for _ in range(len(sorted_rows))]
        top = left_corner[1]
        bottom = right_corner[3]
        for xmin, ymin, xmax, ymax, text in table.text_positions(remove_table_offset=True):
            yavg = (ymin + ymax) / 2
            i = int((yavg - top) / (bottom - top) * len(sorted_rows))
            if 0 <= i < len(bins):
                bins[i].append(yavg)
        known_means = [np.mean(x) for x in bins if len(x)]
        
        differences = [known_means[i+1] - known_means[i] for i in range(len(known_means) - 1)]
        known_height = np.median(differences)
        
        # means are within 0.2 * known_height of each other, consolidate them
        i = 1
        while i < len(known_means):
            prev = known_means[i-1]
            cur = known_means[i]
            if abs(cur - prev) < 0.2 * known_height:
                # merge by averaging
                known_means[i-1] = (prev + cur) / 2
                known_means.pop(i)
                
                # don't allow double merging
            i += 1
        
        sorted_rows = _guess_row_bboxes_for_large_tables(table, config, sorted_rows, sorted_headers, 
                known_means=known_means, known_height=known_height)
        
    # nms takes care of deduplication
    
    table.effective_rows = sorted_rows
    table.effective_columns = sorted_columns
    table.effective_headers = sorted_headers
    table.effective_projecting = sorted_projecting
    table.effective_spanning = spanning_cells
    
    # 4b. check for catastrophic overlap
    total_column_area = 0
    for col in sorted_columns:
        if col['label'] == 'table column':
            total_column_area += (col['bbox'][2] - col['bbox'][0]) * (col['bbox'][3] - col['bbox'][1])
    # we must divide by 2, because a cell is counted twice by the row + column
    total_area = (total_row_area + total_column_area) / 2
    
    if total_area > (1 + config.total_overlap_reject_threshold) * table_area:
        raise ValueError(f"The identified boxes have significant overlap: {total_area / table_area - 1:.2%} of area is overlapping (Max is {config.total_overlap_reject_threshold:.2%})")
    
    elif total_area > (1 + config.total_overlap_warn_threshold) * table_area:
        outliers['high overlap'] = (total_area / table_area - 1)
    
        
    column_headers = {}
        
    # in case of large_table_guess, keep track of the means of rows
    row_means = None
    if large_table_guess:
        row_means = [[] for _ in range(len(sorted_rows))]
    


    table_array = _fill_using_partitions(table.text_positions(remove_table_offset=True), config=config, 
                                        sorted_rows=sorted_rows, sorted_columns=sorted_columns, 
                                        outliers=outliers, row_means=row_means)
    
    
    num_rows = len(sorted_rows)
    num_columns = len(sorted_columns)
    
    # create a pandas dataframe from the table array
    
    header_indices, projecting_indices = _determine_headers_and_projecting(sorted_rows, sorted_headers, sorted_projecting)

    # extract out the headers
    header_rows = table_array[header_indices]
    if config.enable_multi_indices and len(header_rows) > 1:
        # Convert header rows to a list of tuples, where each tuple represents a column
        columns_tuples = list(zip(*header_rows))

        # Create a MultiIndex with these tuples
        column_headers = pd.MultiIndex.from_tuples(columns_tuples, names=[f"Header {len(header_rows)-i}" for i in range(len(header_rows))])
        # Level is descending from len(header_rows) to 1

    else:
        # join by '\n' if there are multiple lines
        column_headers = [' \\n'.join([row[i] for row in header_rows if row[i]]) for i in range(num_columns)]
    # note: header rows will be taken out
    table._df = pd.DataFrame(data=table_array, columns=column_headers)
    
    # a. mark as projecting/non-projecting
    is_projecting = [x in projecting_indices for x in range(num_rows)]
    if any(is_projecting):
        # insert at end
        table._df.insert(num_columns, 'is_projecting_row', is_projecting)
    
    # b. drop the former header rows always
    table._df.drop(index=header_indices, inplace=True)
    table._df.reset_index(drop=True, inplace=True)
    
    if config.remove_null_rows:
        keep_columns = [n for n in table._df if n != 'is_projecting_row']
        table._df.dropna(subset=keep_columns, how='all', inplace=True)
    table.outliers = outliers
    return table._df