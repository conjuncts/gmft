from gmft.algorithm.dividers import _ioa


def pairwise(iterable):
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
    sorted_projecting, 
    iob_threshold=0.7
):
    """
    Separates the sorted_horizontals into rows, headers, and projecting rows.
    Then, identifies a list of indices of headers and projecting rows.

    Formerly called _determine_headers_and_projecting

    :param row_intervals: list of dividers, including endbounds
    :param top_header_y: y value which separates the top header from the rest of the table
    :param sorted_projecting: list of bboxes (x0, y0, x1, y1) of projecting rows
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
            for _, proj_y0, _, proj_y1 in sorted_projecting
        ):
            projecting_indices.append(i)
            continue

    return header_indices, projecting_indices