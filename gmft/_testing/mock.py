from gmft.core.words_list import WordsList
from gmft.reformat.schema import Partitions, TableStructureWithWords


def typeset_words(words: list[list[str]], top_n_header=1) -> TableStructureWithWords:
    """
    Sets the words in a table structure.

    :param words: List of lists, where each inner list represents a row of words.
    :param top_n_header: Number of rows to treat as header rows.
    """

    width = max(len(word) for word in words)
    height = len(words)

    column_char_widths = {}
    row_char_heights = {}

    for i in range(width):
        # number of characters in each column
        column_char_widths[i] = max(len(row[i] or "") for row in words if len(row) > i)

    for i, row in enumerate(words):
        # number of lines in each cell
        row_char_heights[i] = max((cell or "").count('\n') for cell in row) + 1

    HORIZ_UNIT = 5  # Width of each character in the grid
    VERT_UNIT = 10  # Height of each character in the grid

    # generate grid structure
    x_values = []
    x_cursor = 0
    for i in range(width):
        x_values.append(x_cursor)
        x_cursor += HORIZ_UNIT * (column_char_widths[i] + 1)
    
    y_values = []
    y_cursor = 0
    for i in range(height):
        y_values.append(y_cursor)
        y_cursor += VERT_UNIT * (row_char_heights[i] + 1)

    # The bboxes are separated by, at minimum, HORIZ_UNIT or VERT_UNIT.
    
    bboxes = []
    h_splits = [0]
    v_splits = [0]
    for i, row in enumerate(words):
        for j, cell in enumerate(row):
            if cell is None:
                continue
            x = x_values[j]
            y = y_values[i]

            # cell-wise width/height
            w = HORIZ_UNIT * len(cell or "")
            h = VERT_UNIT * ((cell or "").count('\n') + 1)
            bboxes.append((x, y, x + w, y + h, cell))
    
    x_padding = HORIZ_UNIT // 2 # aim to split the extra
    for i, x in enumerate(x_values):
        # find the maximum width
        w = HORIZ_UNIT * column_char_widths[i]

        v_splits.append(x + w + x_padding)
    
    y_padding = VERT_UNIT // 2
    for i, y in enumerate(y_values):
        h = VERT_UNIT * row_char_heights[i]
        h_splits.append(y + h + y_padding)


    if top_n_header < len(h_splits):
        top_header_y = h_splits[top_n_header]
    else:
        top_header_y = h_splits[-1]

    result = TableStructureWithWords(
        words=WordsList._from_text_positions(bboxes),
        locations=Partitions(
            row_dividers=h_splits,
            col_dividers=v_splits,
            top_header_y=top_header_y,
            left_header_x=0,
            projected=[],
            spanning=[]  # No spanning cells in this mock
        ),
    )
    return result
