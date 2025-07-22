from typing import Generator, Tuple

from gmft.base import Rect


def _rotate_generator(
    _generator: Generator[Tuple[float, float, float, float, str], None, None],
    angle: int,
    table_rect: Rect,
):
    if angle == 0:
        yield from _generator
    elif angle == 90:
        for w in _generator:
            x0, y0, x1, y1, text = w[:5]
            x0, y0, x1, y1 = table_rect.height - y1, x0, table_rect.height - y0, x1
            yield (x0, y0, x1, y1, text, *w[5:])
    elif angle == 180:
        for w in _generator:
            x0, y0, x1, y1, text = w[:5]
            x0, y0, x1, y1 = (
                table_rect.width - x1,
                table_rect.height - y1,
                table_rect.width - x0,
                table_rect.height - y0,
            )
            yield (x0, y0, x1, y1, text, *w[5:])
    elif angle == 270:
        for w in _generator:
            x0, y0, x1, y1, text = w[:5]
            x0, y0, x1, y1 = y0, table_rect.width - x1, y1, table_rect.width - x0
            yield (x0, y0, x1, y1, text, *w[5:])
