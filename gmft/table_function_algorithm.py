
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
    if not isinstance(bbox1, (tuple, list)): # intended to be a Rect
        bbox1 = bbox1.bbox
    if not isinstance(bbox2, (tuple, list)): # intended to be a Rect
        bbox2 = bbox2.bbox
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

def _symmetric_iob_for_columns(bbox1, bbox2):
    """
    Modification of iob but for columns: pretend that the bboxes are infinitely tall. For min of bbox1 and bbox2.
    """
    a0, a1 = bbox1[0], bbox1[2]
    b0, b1 = bbox2[0], bbox2[2]
    
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
    # from bisect.bisect_left; copy the code to support key_func in python < 3.10
    a = sorted_list
    x = value
    lo = 0
    hi = len(a) # None
    
    # Note, the comparison uses "<" to match the
    # __lt__() logic in list.sort() and in heapq.
    if key_func is None:
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] < x:
                lo = mid + 1
            else:
                hi = mid
    else:
        while lo < hi:
            mid = (lo + hi) // 2
            if key_func(a[mid]) < x:
                lo = mid + 1
            else:
                hi = mid
    return lo
    # return bisect.bisect_left(sorted_list, value, key=key_func)



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


def _fill_in_gaps(sorted_rows, gap_height, leave_gap=0.4, top_of_table=None):
    """
    top_y: intend to create an extra row above the first row, if there is a gap.
    """
    # fill in gaps in the rows
    margin = leave_gap * gap_height
    
    if top_of_table is not None and len(sorted_rows):
        if sorted_rows[0]['bbox'][1] - top_of_table > gap_height:
            # fill in the gap
            print("Filling in gap at top of table")
            sorted_rows.insert(0, {'confidence': 1, 'label': 'table row', 'bbox': 
                                   [sorted_rows[0]['bbox'][0], top_of_table, sorted_rows[0]['bbox'][2], sorted_rows[0]['bbox'][1] - margin]})
    
    i = 1
    while i < len(sorted_rows):
        prev = sorted_rows[i-1]
        cur = sorted_rows[i]
        if cur['bbox'][1] - prev['bbox'][3] > gap_height:
            # fill in the gap
            sorted_rows.insert(i, {'confidence': 1, 'label': 'table row', 'bbox': 
                                   [prev['bbox'][0], prev['bbox'][3] + margin, prev['bbox'][2], cur['bbox'][1] - margin]})
        i += 1
    

def _non_maxima_suppression(sorted_rows: list[dict], overlap_threshold=0.1):
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
    
def _is_within_header(bbox, sorted_headers, _iob=_iob_for_rows, header_threshold=0.5): # assume len(sorted_headers) <= 2
    """
    check if bbox is in any of the bboxes specified in sorted_headers
    sorted_headers: list of dictionaries, each with keys 'bbox', 'confidence', 'label'
    """
    return any(_iob(bbox, header['bbox']) > header_threshold for header in sorted_headers)
    
def _is_within_any_bbox(needle: tuple[float, float, float, float], haystack: list[tuple[float, float, float, float]], _iob=_iob_for_rows, threshold=0.5): # assume len(sorted_headers) <= 2
    """
    check if needle bbox is in any of haystack bboxes
    """
    return any(_iob(needle, bbox) > threshold for bbox in haystack)

def _guess_row_bboxes_for_large_tables(table: TATRFormattedTable, config: TATRFormatConfig, sorted_rows, sorted_headers, row_height, known_means=None):
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
            if _is_within_header(row, sorted_headers):
                new_rows.append(sorted_rows.pop(0))
            else:
                break
        if not sorted_rows:
            # all rows are headers
            return new_rows
    y = sorted_rows[0]['bbox'][1]
        

    # fail-safe: if it predicts a very large table, raise
    est_num_rows = (table_ymax - y) / row_height
    if est_num_rows > config.large_table_maximum_rows:
        if config.verbosity >= 1:
            print(f"Estimated number of rows {est_num_rows} is too large")
        table.outliers['excessive rows'] = max(table.outliers.get('excessive rows', 0), est_num_rows)
        row_height = (table_ymax - y) / 100
    
    if known_means:
        # print(known_means)
        # construct rows, trying to center the rows on the known means
        starting_y = y
        prev_height = None
        for i, mean in enumerate(known_means):
            if mean < starting_y:
                # do not observe the header
                continue
            y = mean - row_height / 2
            # do NOT construct mini row if there is a gap
            # if prev_height is not None and y < prev_height:
                # new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, prev_height, rightmost, y]})
            new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, y, rightmost, y + row_height]})
            prev_height = y + row_height
            
    else:
        # this is reminiscent of the proof that the rationals are dense in the reals
        while y < table_ymax:
            new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, y, rightmost, y + row_height]})
            y += row_height
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

    

def _determine_headers_and_projecting(sorted_rows, sorted_headers, sorted_projecting, outliers=None):
    """
    Splits the sorted_horizontals into rows, headers, and projecting rows. 
    Then, identifies a list of indices of headers and projecting rows.
    """
    
    # determine which rows overlap (> 0.9) with headers
    header_indices = []
    projecting_indices = []
    
    # if sorted_rows and sorted_headers:
    #     first_row = sorted_rows[0]
    #     first_header = sorted_headers[0]
    #     if first_row['bbox'][1] - 1 > first_header['bbox'][3]:
    #         # try to detect when the header is not included in the rows
    #         if _iob(first_header['bbox'], first_row['bbox']) < 0.5: # the header is not in a row
    #             if outliers is not None:
    #                 outliers['header_is_not_row'] = True
                # print("The header is not included as a row. Consider adding it back as a row.")
    
    for i, row in enumerate(sorted_rows):
        # TODO binary-ify
        if _is_within_header(row['bbox'], sorted_headers):
            header_indices.append(i)
        if any(_iob(row['bbox'], proj['bbox']) > 0.7 for proj in sorted_projecting):
            projecting_indices.append(i)
    return header_indices, projecting_indices

def _find_all_rows_for_box(sorted_rows: list[tuple], bbox, threshold=0, _iob=_iob_for_rows):
    """
    Find all rows that intersect with the box.
    :param sorted_rows: list of bboxes, so list of tuples (xmin, ymin, xmax, ymax)
    :return list of indices of rows
    """
    rows = []
    _, ymin, _, ymax = bbox
    # linsearch
    # for i, row in enumerate(sorted_rows):
    i = _find_leftmost_gt(sorted_rows, ymin, lambda row: row[3]) # ['bbox'][3])
    while i < len(sorted_rows):
        row = sorted_rows[i]
        iob_score = _iob(bbox, row) # ['bbox'])

        if iob_score > threshold:
            rows.append(i)
        # we may break early when the row is below the textbox
        # this assumes that row_min and row_max are roughly 
        if ymax < row[1]: # ['bbox'][1]: # ymax < row_min
            break
        i += 1
    return rows

def _find_all_columns_for_box(sorted_columns: list[tuple], bbox, threshold=0, _iob=_iob_for_columns):
    """
    Find all columns that intersect with the box.

    :param sorted_columns: list of bboxes, so list of tuples (xmin, ymin, xmax, ymax)
    """
    columns = []
    xmin, _, xmax, _ = bbox
    # linsearch
    # for i, row in enumerate(sorted_columns):
    i = _find_leftmost_gt(sorted_columns, xmin, lambda bbox: bbox[2]) # column: column['bbox'][2])
    while i < len(sorted_columns):
        column = sorted_columns[i]
        iob_score = _iob(bbox, column) # column['bbox'])
        if iob_score > threshold:
            columns.append(i)
        if xmax < column[0]: # column['bbox'][0]: # xmax < column_min
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


def _split_spanning_cells(spanning_cells: list[dict], sorted_headers_bboxes: list[tuple[float, float, float, float]], 
                          sorted_rows: list[tuple[float, float, float, float]], sorted_columns: list[tuple[float, float, float, float]], 
                          header_indices: list[int]) -> tuple[list[dict], list[dict], list[dict]]:
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
    """
    sorted_hier_top_headers = []
    sorted_monosemantic_top_headers = []
    sorted_hier_left_headers = []
    for x in spanning_cells:
        # if _is_within_header(x['bbox'], sorted_headers): # , _iob=_iob):
        if _is_within_any_bbox(x['bbox'], sorted_headers_bboxes, _iob=_iob):
            # good - it is located in the header
            # if calculate_semantic_column_headers:
            all_valid_rows = _find_all_rows_for_box(sorted_rows, x['bbox'], threshold=0.2)
            
            # problem: we actually want to divide by the _column_ width, not the bbox
            # since the bbox is wider
            all_valid_cols = _find_all_columns_for_box(sorted_columns, x['bbox'], threshold=0.2, 
                    _iob=_symmetric_iob_for_columns)

            # if it only spans only 1 row, then it is a hierarchical top header
            all_valid_rows = [x for x in all_valid_rows if x in header_indices]
            if len(all_valid_rows) == 1 and len(all_valid_cols) > 1:
                
                copy_x = {
                    'row_idx': all_valid_rows[0],
                    'col_indices': all_valid_cols,
                    **x
                }
                sorted_hier_top_headers.append(copy_x)
            elif len(all_valid_cols) == 1 and len(all_valid_rows) > 1:
                # this suggests that it is a non-hierarchical column header where the one title
                # has a newline in it
                copy_x = {
                    'col_idx': all_valid_cols[0],
                    'row_indices': all_valid_rows,
                    **x
                }
                sorted_monosemantic_top_headers.append(copy_x)
            # else:
                # sorted_hier_top_headers.append(x)
        else:
            # if calculate_semantic_row_headers:
            all_valid_cols = _find_all_columns_for_box(sorted_columns, x['bbox'], threshold=0.2)
            
            
            # further require that it spans only 1 column
            if len(all_valid_cols) == 1:
                col_idx = all_valid_cols[0]
                # bbox may be taller than each row, so use symmetric iob
                all_valid_rows = _find_all_rows_for_box(sorted_rows, x['bbox'], threshold=0.2, 
                                        _iob=_symmetric_iob_for_rows)
                copy_x = {
                    'col_idx': col_idx,
                    'row_indices': all_valid_rows,
                    **x
                }
                sorted_hier_left_headers.append(copy_x)
            # else:
            #     sorted_hier_left_headers.append(x)
    
    # sort hier_left_headers by ascending y0
    # which is advantageous becauseit makes it closer to algo fill
    sorted_hier_left_headers.sort(key=lambda x: x['bbox'][1])

    return sorted_hier_top_headers, sorted_monosemantic_top_headers, sorted_hier_left_headers

def _semantic_spanning_fill(table_array, sorted_hier_top_headers: list[dict], sorted_monosemantic_top_headers: list[dict], 
                            sorted_hier_left_headers: list[dict], header_indices: list[int], config):
    """
    Fill the table array according to semantic information from detected spanning cells.
    (Assumes that NMS has already been applied, and there are no conflicts)
    """
    
    _hier_left_indices = [] # keep track of columns for the user
    # Fill hierarchical left headers
    # 1. assume that only one cell is filled. 
    # We may also possibly assume that only the top cell should be non-empty
    # We could also assume that this only applies to the leftmost column
    # -- multiple subdivisions, like pdf6_t0 is possible
    # 2. then, copy among all cells
    if config.semantic_hierarchical_left_fill == 'deep':
        perform_changes = [] # list of {col_num: int, content: str, row_nums: list[int]}
        for x in sorted_hier_left_headers:

            col_num = x['col_idx']
            last_found = None # assume that there is a unique text

            # CHANGES in 4.0: 
            # - make it more safe by fixing a bug where it would overwrite data
            # - it handles overlapping cells better by
            # only making changes at the end. This helps in the common case
            # by sorting the list top to bottom, 
            # which gives similar behavior to the 'algorithm'
            # downwards (no merging)
            first_invalid_i = len(x['row_indices'])
            for i, row_num in enumerate(x['row_indices']):
                cell_content = table_array[row_num, col_num]
                if cell_content:
                    # do not overwrite stuff - only allow one cell
                    if last_found is None:
                        last_found = cell_content
                    else:
                        # two cells with text
                        first_invalid_i = i
                        break
            if last_found:
                perform_changes.append({'col_num': col_num, 'content': last_found, 'row_nums': x['row_indices'][:first_invalid_i]})
            # if last_found:
            #     for row_num in x['row_indices'][:first_invalid_row]:
            #         if cell_content is None:
            #             table_array[row_num, col_num] = last_found
        
        # now perform changes
        for x in perform_changes:
            col_num = x['col_num']
            content = x['content']
            for row_num in x['row_nums']:
                # to be safe, only fill in nones
                if table_array[row_num, col_num] is None:
                    table_array[row_num, col_num] = content
            
    elif config.semantic_hierarchical_left_fill == 'algorithm':
        # get counts of all column indices, then keep those >= 2
        col_counts = {}
        for x in sorted_hier_left_headers:
            col_num = x['col_idx']
            col_counts[col_num] = col_counts.get(col_num, 0) + 1
        
        # only expect leftmost 3 columns and more than 2 such spanning items.
        _hier_left_indices = [k for k, v in col_counts.items() if k < 3 and v >= 2]
        
        first_row = max(header_indices, default=-1) + 1
        
        content = None
        for col_num in _hier_left_indices:
            for row_num in range(first_row, table_array.shape[0]):
                if table_array[row_num, col_num] is not None:
                    content = table_array[row_num, col_num]
                else:
                    table_array[row_num, col_num] = content
        
    
                

    
    # Fill hierarchical top headers
    # 1. This time, aggregate
    # 2. then, copy among all cells
    for x in sorted_hier_top_headers:
        row_num = x['row_idx']
        content = [] # this time, aggregate, and copy among all cells
        for col_num in x['col_indices']:
            cell_content = table_array[row_num, col_num]
            if cell_content:
                content.append(cell_content)
        if content:
            content = ' '.join(content)
            for col_num in x['col_indices']:
                table_array[row_num, col_num] = content
            
        
    # Fill monosemantic top headers - so these are unhierarchical column headers that are all 
    # contained in one column
    # 0. There is only something to do when text is in both these cells
    # 1. This time, aggregate
    # 2. Only write to the bottom-most cell
    # for now, less useful
    for x in sorted_monosemantic_top_headers:
        col_num = x['col_idx']
        content = [] # this time, aggregate, and push it all to the bottom-most cell
        for row_num in x['row_indices']:
            cell_content = table_array[row_num, col_num]
            if cell_content:
                content.append(cell_content)
        if len(content) > 1:
            # TODO config options for "repeat", "bottom"
            # if config.enable_multi_header:
                # duplicate
                # for row_num in x['row_indices']:
                    # table_array[row_num, col_num] = ' \\n'.join(content)
            # else:
                # if not multi-header:
                # write once, wipe the other cells
            for row_num in x['row_indices']:
                table_array[row_num, col_num] = None
            # push it all to the bottom-most cell
            bottom_most_row = x['row_indices'][-1]
            table_array[bottom_most_row, col_num] = ' \\n'.join(content)
    
    return _hier_left_indices
                
        

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
        
        # score_norm_deviation = abs(row_max_iob * column_max_iob - score) / score
        # if score_norm_deviation > config.corner_clip_outlier_threshold:
            # outliers['corner clip'] = True
        
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
    #     if _symmetric_iob(prev['bbox'], cur['bbox']) > config.deduplication_iob_threshold:
    sorted_rows, sorted_headers, sorted_projecting = _split_sorted_horizontals(sorted_horizontals)
    
    _non_maxima_suppression(sorted_projecting, overlap_threshold=config._nms_overlap_threshold)
    # non-maxima suppression
    num_removed = _non_maxima_suppression(sorted_rows, overlap_threshold=config._nms_overlap_threshold)
    if num_removed > 0 and config.verbosity >= 2:
        print(f"Removed {num_removed} overlapping rows")
    if num_removed > config.nms_warn_threshold:
        outliers['nms removed rows'] = max(outliers.get('nms removed rows', 0), num_removed)
    
    _widen_and_even_out_rows(sorted_rows, sorted_headers)
    
    word_height = table.predicted_word_height(smallest_supported_text_height=config._smallest_supported_text_height)
    
    # fill in a header gap, if it exists (ie. if the header is not included in the rows)
    top_of_table = None
    if sorted_headers:
        top_of_table = sorted_headers[0]['bbox'][1]
    _fill_in_gaps(sorted_rows, word_height, top_of_table=top_of_table)
    
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
        if config.verbosity >= 2:
            print("Invoking large table row guess! set TATRFormatConfig.force_large_table_assumption to False to disable this.")
        
        sorted_rows = _guess_row_bboxes_for_large_tables(table, config, sorted_rows, sorted_headers, row_height=word_height)
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
        known_means = [float(np.mean(x)) for x in bins if len(x)]
        
        if not known_means:
            # no text was detected
            outliers['no text'] = True
            table.effective_rows = []
            table.effective_columns = []
            table.effective_headers = []
            table.effective_projecting = []
            table.effective_spanning = []
            table._top_header_indices = []
            table._projecting_indices = []
            table._hier_left_indices = []
            table._df = pd.DataFrame()
            table.outliers = outliers
            return table._df
        
        differences = [known_means[i+1] - known_means[i] for i in range(len(known_means) - 1)]
        if len(differences):
            known_height = float(np.median(differences))
        else:
            # if there is only one row, then we're stuck. set to table height.
            known_height = bottom - top
        
        # means are within 0.2 * known_height of each other, consolidate them
        # actually no - use 0.6 * WORD_HEIGHT 
        i = 1
        while i < len(known_means):
            prev = known_means[i-1]
            cur = known_means[i]
            if abs(cur - prev) < config._large_table_merge_distance * word_height: # default: 0.2
                # merge by averaging
                known_means[i-1] = (prev + cur) / 2
                known_means.pop(i)
                
                # don't allow double merging
            i += 1
        
        sorted_rows = _guess_row_bboxes_for_large_tables(table, config, sorted_rows, sorted_headers, 
                known_means=known_means, row_height=known_height)
        
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
        # this shouldn't really happen anymore with NMS
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
    
    

    
    # create a pandas dataframe from the table array
    
    # delete empty rows
    if config.remove_null_rows:
        keep_rows = [n for n in range(len(sorted_rows)) if any(x is not None for x in table_array[n, :])]
        table_array = table_array[keep_rows]
        sorted_rows = [sorted_rows[n] for n in keep_rows]
    
    num_rows = len(sorted_rows)
    num_columns = len(sorted_columns)
    
    # find indices of key rows
    header_indices, projecting_indices = _determine_headers_and_projecting(sorted_rows, sorted_headers, sorted_projecting, outliers=outliers)

    # semantic spanning fill
    if config.semantic_spanning_cells:
        sorted_headers_bboxes = [x['bbox'] for x in sorted_headers]
        sorted_row_bboxes = [x['bbox'] for x in sorted_rows]
        sorted_column_bboxes = [x['bbox'] for x in sorted_columns]
        sorted_hier_top_headers, sorted_monosemantic_top_headers, sorted_hier_left_headers = _split_spanning_cells(spanning_cells, sorted_headers_bboxes, sorted_row_bboxes, sorted_column_bboxes, header_indices)
        _non_maxima_suppression(sorted_hier_top_headers, overlap_threshold=config._nms_overlap_threshold)
        _non_maxima_suppression(sorted_monosemantic_top_headers, overlap_threshold=config._nms_overlap_threshold)
        _non_maxima_suppression(sorted_hier_left_headers, overlap_threshold=config._nms_overlap_threshold)
        hier_left_idxs = _semantic_spanning_fill(table_array, sorted_hier_top_headers, sorted_monosemantic_top_headers, sorted_hier_left_headers,
                header_indices=header_indices,
                config=config)
        table._hier_left_indices = hier_left_idxs 
    else:
        table._hier_left_indices = [] # for the user
    
    # technically these indices will be off by the number of header rows ;-;
    if config.enable_multi_header:
        table._top_header_indices = header_indices
    else:
        table._top_header_indices = [0] if header_indices else []

    
    # extract out the headers
    header_rows = table_array[header_indices]
    if config.enable_multi_header and len(header_rows) > 1:
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
    if projecting_indices:
        is_projecting = [x in projecting_indices for x in range(num_rows)]
        # remove the header_indices
        # TODO this could be made O(n)
        is_projecting = [x for i, x in enumerate(is_projecting) if i not in header_indices]
        table._projecting_indices = [i for i, x in enumerate(is_projecting) if x]
    
    # if projecting_indices:
        # insert at end
        # table._df.insert(num_columns, 'is_projecting_row', is_projecting)
    
    # b. drop the former header rows always
    table._df.drop(index=header_indices, inplace=True)
    table._df.reset_index(drop=True, inplace=True)
    
    # if config.remove_null_rows:
    #     keep_columns = [n for n in table._df if n != 'is_projecting_row']
    #     table._df.dropna(subset=keep_columns, how='all', inplace=True)
    table.outliers = outliers
    return table._df