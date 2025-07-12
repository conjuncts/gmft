from typing import List, Literal, Optional, TypedDict

class TextBbox(TypedDict):
    """
    TypedDict for a text bounding box.
    """

    text: str

    xmin: float
    ymin: float
    xmax: float
    ymax: float

class TableTextBbox(TextBbox):
    """
    TypedDict for a text bounding box that lives in a table.
    """

    row_idx: int
    col_idx: int

class FineTextBbox(TextBbox):
    """
    Text bounding box with more fine-grained properties.
    """

    block_idx: int
    line_idx: int
    word_idx: int

    direction: Literal["ltr", None]
    hyphen_parts: Optional[List["FineTextBbox"]]
    """
    If text is hyphenated, this will contain bboxes of individual
    hyphenated parts. Otherwise, it will be None.
    """
