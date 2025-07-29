from gmft._testing.mock import typeset_words
from gmft.algorithm.structure_rewrite import (
    _execute_cell_merges,
    fill_2d_array,
    generate_mergers,
)


def test_alpha_grid():
    """
    Make `fill_2d_array` regenerate the original grid.
    """
    grid = [
        ["a", None, "b", None, None],
        ["c", "d", "e", "f", "g"],
        ["h", "i", "j", None, "k"],
        ["l", "m", "n", "o", "p"],
        ["q", "r", "s", "t", "u"],
        ["v", "w", "x", "y", "z"],
    ]

    words_struct = typeset_words(grid, top_n_header=2)

    arraigned = fill_2d_array(words_struct)

    assert arraigned.table_array == grid


def test_span_operations():
    """
    Various actions on spans.
    """
    grid = [
        # x=[0,5] [10,15] [20,25] [30,35] [40,45]
        # x_cuts= 0 7 17 27 37 47
        ["a", None, None, "b", "+"],  # y=[0,10]
        ["c", "d", "e", "f", "g"],  # y=[20,30]
        # ------------------------ y=35
        ["h", "i", "j", None, "k"],  # y=[40,50]
        [None, "m", "n", "o", "p"],  # y=[60,70]
        ["q", None, "s", "t", "u"],  # y=[80,90]
        [None, "w", "x", "y", "z"],  # y=[100,110]
        [None, None, "A", "B", "C"],  # y=[120,130]
        ["D", "E", "F", "G", "H"],  # y=[140,150]
        # y_cuts= 0 15 35 55 75 95 115
    ]

    words_struct = typeset_words(grid, top_n_header=2)
    words_struct.locations.spanning = [
        {
            "confidence": 0.9,
            "label": "table spanning cell",
            "bbox": (0.1, 0.1, 18, 5),  # top hier, "A"
        },
        {
            "confidence": 0.9,
            "label": "table spanning cell",
            "bbox": (40, 0, 45, 30),  # top nonhier, "+g"
        },
        {
            "confidence": 0.8,
            "label": "table spanning cell",
            "bbox": (0, 42, 10, 68),  # left hier, slightly shrunk
        },
        {
            "confidence": 0.8,
            "label": "table spanning cell",
            "bbox": (0, 78, 10, 138),  # left hier, slightly expanded
        },
        {
            "confidence": 0.8,
            "label": "table spanning cell",
            "bbox": (10, 35, 20, 150),  # left hier, fill
        },
        # NMS bboxes should be ignored
        {
            "confidence": 0.1,
            "label": "table spanning cell",
            "bbox": (0, 0, 400, 5),  # should be cls as top hier
        },
    ]

    arranged = fill_2d_array(words_struct)
    arranged = generate_mergers(arranged, _nms_overlap_threshold=0.2)

    arranged = _execute_cell_merges(arranged)

    print(arranged.table_array)

    expected = [
        ["a", "a", None, "b", None],
        ["c", "d", "e", "f", "+ g"],
        # ------------------------ y=35
        ["h", "i", "j", None, "k"],
        ["h", "m", "n", "o", "p"],
        ["q", "m", "s", "t", "u"],
        ["q", "w", "x", "y", "z"],
        ["q", "w", "A", "B", "C"],
        ["D", "E", "F", "G", "H"],
    ]
    assert arranged.table_array == expected
