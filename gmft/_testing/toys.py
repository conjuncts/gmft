from gmft._testing.mock import typeset_words


def _large_span_example_table():
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
    return grid, words_struct
