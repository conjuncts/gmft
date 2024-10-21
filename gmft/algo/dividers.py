

import bisect
from typing import Generator

import numpy as np


def find_row_for_target(row_dividers, ytarget):
    """
    Find the row that a box belongs to, according to the row dividers.
    The row_dividers do not include endbounds.
    """
    return bisect.bisect_left(row_dividers, ytarget)

def find_column_for_target(column_dividers, xtarget):
    """
    Find the column that a box belongs to, according to the column dividers.
    The column_dividers do not include endbounds.
    """
    return bisect.bisect_left(column_dividers, xtarget)

# def find_rows_for_interval(row_dividers, table_bounds, yinterval, threshold=0):
#     """
#     Find the rows that intersect with the interval by at least threshold.
#     Assume that yinterval is larger, and therefore the ioa is divided by the row size.

#     Returns list of indices, with domain [0, len(row_dividers)+1]
#     """
#     leftmost = bisect.bisect_left(row_dividers, yinterval[0])
#     rightmost = bisect.bisect_right(row_dividers, yinterval[1])

#     # valid rows are [leftmost, rightmost], inclusive
#     # now filter by threshold
#     if threshold == 0:
#         return list(range(leftmost, rightmost+1))
#     valid_rows = []
#     consider = [table_bounds[1]] + row_dividers + [table_bounds[3]] # len: len(row_dividers) + 2
#     for i in range(leftmost, rightmost+1):
#         row_y_interval = (consider[i], consider[i+1])
#         if _ioa(row_y_interval, yinterval) > threshold:
#             valid_rows.append(i)

def _find_all_intervals_for_interval(sorted_intervals, interval, threshold=0):
    """
    Find all intervals that intersect with the interval.
    """
    start, end = interval
    left = bisect.bisect_right([i[1] for i in sorted_intervals], start)
    right = bisect.bisect_left([i[0] for i in sorted_intervals], end)
    
    result = sorted_intervals[left:right]
    if threshold == 0:
        return result
    return [x for x in result if _ioa(x, interval) > threshold]

def fill_using_true_partitions(text_positions: Generator[tuple[float, float, float, float, str], None, None], 
                          row_dividers: list[dict], column_dividers: list[dict], table_bounds: tuple[float, float, float, float]):
    """
    Given estimated positions of text positions,
    row dividers (does not include endbounds), column dividers (does not include endbounds),
    fills the table array.

    assumes dividers are sorted
    """

    num_rows = len(row_dividers) + 1
    num_columns = len(column_dividers) + 1
    table_array = np.empty([num_rows, num_columns], dtype="object")

    for xmin, ymin, xmax, ymax, text in text_positions:
        
        # 5. let row_num be row with max iob
        xtarget = (xmin + xmax) / 2
        ytarget = (ymin + ymax) / 2

        # if completely outside the bounds (no intersection), ignore
        if not (table_bounds[0] <= xtarget <= table_bounds[2] and table_bounds[1] <= ytarget <= table_bounds[3]):
            continue

        # to find x, we need the first column divider (moving LTR) where xtarget < xdivider

        column_num = find_column_for_target(column_dividers, xtarget)
        # then, it belongs to the xi-th column of the np array (no off by 1 error)

        row_num = find_row_for_target(row_dividers, ytarget)
        
        if table_array[row_num, column_num] is not None:
            table_array[row_num, column_num] += ' ' + text
        else:
            table_array[row_num, column_num] = text
    
    return table_array

def _ioa(a: tuple[float, float], b: tuple[float, float]) -> float:
    """
    Calculate the intersection of (closed) intervals, divided by the first interval a.
    
    If a is a single point [x, x], then return 1 if x is in the interior of b, 0 otherwise.
    """
    a0, a1 = a
    b0, b1 = b
    if a0 > b1 or a1 < b0:
        return 0
    if a0 == a1:
        return 1 if b0 < a0 < b1 else 0
    
    return (min(a1, b1) - max(a0, b0)) / (a1 - a0)

def get_good_between_dividers(dividers: list[tuple[float, float]], min_val: float, max_val: float, add_inverted=True):
    """
    Get the good content between dividers.
    
    :param dividers: list of dividers, each a tuple of form (start, end).
    :param rows: only 
    """
    result = []

    prev_end = min_val
    for i, (start, end) in enumerate(dividers):
        if start > prev_end:
            result.append((prev_end, start))
        else:
            if add_inverted:
                # begrudgingly add the inverted interval (psuedo-row, which is likely very thin) to keep things balanced
                result.append((start, prev_end))
            else:
                pass
        prev_end = end
    
    # the last interval
    if prev_end < max_val:
        result.append((prev_end, max_val))
    else:
        if add_inverted:
            result.append((max_val, prev_end))
    return result