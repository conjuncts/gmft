from gmft._testing.mock import typeset_words
from gmft.algorithm.structure_rewrite import _to_polars, export_header, fill_2d_array

import polars as pl
from polars.testing import assert_frame_equal

def test_construct_df():
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
    col_headers = export_header(arraigned, enable_multi_header=False)
    df = _to_polars(arraigned, column_headers=col_headers)

    expected = pl.DataFrame({
        'a \\nc': ['h', 'l', 'q', 'v'],
        'd': ['i', 'm', 'r', 'w'],
        'b \\ne': ['j', 'n', 's', 'x'],
        'f': [None, 'o', 't', 'y'],
        'g': ['k', 'p', 'u', 'z']
    }, orient='row')
    assert_frame_equal(df, expected)