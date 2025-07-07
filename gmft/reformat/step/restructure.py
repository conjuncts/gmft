import copy
from gmft.reformat.state import FormatState


def adjust_indices(sorted_indices, sorted_to_remove):
    """
    indices: list of sorted indices to adjust
    to_remove: list of sorted indices being removed from the array
    Returns: adjusted indices
    """
    if not all(
        sorted_indices[i] <= sorted_indices[i + 1]
        for i in range(len(sorted_indices) - 1)
    ):
        raise ValueError("sorted_indices must be sorted in ascending order")
    if not all(
        sorted_to_remove[i] <= sorted_to_remove[i + 1]
        for i in range(len(sorted_to_remove) - 1)
    ):
        raise ValueError("sorted_to_remove must be sorted in ascending order")

    adjusted = []
    i = j = shift = 0

    while i < len(sorted_indices):
        while j < len(sorted_to_remove) and sorted_to_remove[j] < sorted_indices[i]:
            shift += 1
            j += 1
        adjusted.append(sorted_indices[i] - shift)
        i += 1

    return adjusted


def _drop_empty_rows(
    state: FormatState,
    in_place=False,
):
    """
    Drop empty rows from the FormatState.

    :param state: FormatState object containing the table array and empty rows.
    :param in_place: If True, modifies the state in place.
    """

    if not in_place:
        state = copy.deepcopy(state)

    empty_rows = state.empty_rows
    if not empty_rows:
        return state

    # Adjust other rows indices
    state.header_rows = adjust_indices(state.header_rows, empty_rows)
    state.projected_rows = adjust_indices(state.projected_rows, empty_rows)
    # for row_index in sorted(empty_rows, reverse=True):
    #     state.table_array.pop(row_index)

    # TODO: adjust words DataFrame

    state.empty_rows = []

    return state
