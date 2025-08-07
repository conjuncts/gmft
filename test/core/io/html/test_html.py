import re
from gmft._testing.mock import typeset_words
from gmft._testing.toys import _large_span_example_table
from gmft.algorithm.structure_rewrite import (
    fill_2d_array,
    generate_mergers,
)
from gmft.core.io.html import _to_html


def test_construct_html():
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
    result = _to_html(arraigned).replace(" ", "").replace("\n", "")

    assert result == (
        "<table><thead><tr><th>a</th><th></th><th>b</th><th></th><th></th></tr>"
        "<tr><th>c</th><th>d</th><th>e</th><th>f</th><th>g</th></tr></thead>"
        "<tbody><tr><td>h</td><td>i</td><td>j</td><td></td><td>k</td></tr>"
        "<tr><td>l</td><td>m</td><td>n</td><td>o</td><td>p</td></tr>"
        "<tr><td>q</td><td>r</td><td>s</td><td>t</td><td>u</td></tr>"
        "<tr><td>v</td><td>w</td><td>x</td><td>y</td><td>z</td></tr></tbody></table>"
    )
    # td, th, tr {
    #   border: solid black;
    # }


def test_colspan():
    _, words_struct = _large_span_example_table()

    arranged = fill_2d_array(words_struct)
    arranged = generate_mergers(arranged, _nms_overlap_threshold=0.2)
    # do NOT execute the merges! actually - use AGGREGATE | PUSH_BACKWARD
    # arranged = _execute_cell_merges(arranged)

    result = re.sub(r"\n\s*", "", _to_html(arranged)).strip()

    assert result == (
        '<table><thead><tr><th colspan="2">a</th><th></th><th>b</th><th rowspan="2">+ g</th></tr>'
        "<tr><th>c</th><th>d</th><th>e</th><th>f</th></tr></thead>"
        '<tbody><tr><td rowspan="2">h</td><td rowspan="6">i m w E</td><td>j</td><td></td><td>k</td></tr>'
        "<tr><td>n</td><td>o</td><td>p</td></tr>"
        '<tr><td rowspan="3">q</td><td>s</td><td>t</td><td>u</td></tr>'
        "<tr><td>x</td><td>y</td><td>z</td></tr>"
        "<tr><td>A</td><td>B</td><td>C</td></tr>"
        "<tr><td>D</td><td>F</td><td>G</td><td>H</td></tr></tbody></table>"
    )
