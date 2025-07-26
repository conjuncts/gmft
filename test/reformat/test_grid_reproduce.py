from gmft._testing.mock import typeset_words
from gmft.algorithm.structure_rewrite import fill_2d_array

def test_alpha_grid():
    """
    Make `fill_2d_array` regenerate the original grid.
    """
    grid = [
        ['a', None, 'b', None, None],
        ['c', 'd', 'e', 'f', 'g'],
        ['h', 'i', 'j', None, 'k'],
        ['l', 'm', 'n', 'o', 'p'],
        ['q', 'r', 's', 't', 'u'],
        ['v', 'w', 'x', 'y', 'z'],
    ]


    words_struct = typeset_words(grid, top_n_header=2)

    arraigned = fill_2d_array(words_struct)

    assert arraigned.table_array == grid