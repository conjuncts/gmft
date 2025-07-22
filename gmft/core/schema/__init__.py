from typing import List, Literal, NamedTuple, NotRequired, Optional, Tuple, TypedDict


class WordMetadata(TypedDict):
    """
    Metadata for a certain word (text + its bbox).

    Text itself is not included.
    """

    direction: Literal["ltr", "unk", None]
    is_hyphenated: bool
    """
    If hyphenated, 
    """

    hyphen_parts: NotRequired[List[Tuple[float, float, float, float, str]]]


class FancyWord(NamedTuple):
    """
    NamedTuple for a word (text + its bbox) with more fine-grained metadata.

    (x0, y0, x1, y1, text, direction, is_hyphenated)

    where x0 = xmin, y0 = ymin, x1 = xmax, y1 = ymax.
    """

    x0: float
    y0: float
    x1: float
    y1: float

    text: str
    block_idx: Optional[int]
    line_idx: Optional[int]
    word_idx: Optional[int]

    metadata: Optional[WordMetadata]
