from typing import List, Literal, NamedTuple, NotRequired, Optional, Tuple, TypedDict


class TextBbox(NamedTuple):
    """
    NamedTuple for a text bounding box.

    (x0, y0, x1, y1, text)

    where x0 = xmin, y0 = ymin, x1 = xmax, y1 = ymax.
    """

    x0: float
    y0: float
    x1: float
    y1: float

    text: str


class TableTextBbox(TypedDict):
    """
    TypedDict for a text bounding box that lives in a table.
    """

    text: str

    xmin: float
    ymin: float
    xmax: float
    ymax: float

    row_idx: int
    col_idx: int


class TextBboxMetadata(TypedDict):
    """
    Metadata for a certain text bbox.

    Text itself is not included.
    """

    direction: Literal["ltr", "unk", None]
    is_hyphenated: bool
    """
    If hyphenated, 
    """

    hyphen_parts: NotRequired[List[Tuple[float, float, float, float, str]]]


class FineTextBbox(NamedTuple):
    """
    NamedTuple for a text bounding box with more fine-grained metadata.

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

    metadata: Optional[TextBboxMetadata]
