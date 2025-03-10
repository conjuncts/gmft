from __future__ import annotations  # 3.7


import re
from typing import TYPE_CHECKING, Tuple

import numpy as np

from gmft.common import Rect

if TYPE_CHECKING:
    from gmft.detectors.common import CroppedTable


def _find_gap(
    words,
    init_word_height,
    start_i,
    end_i,
    step=1,
    line_spacing=2.5,
    stop_y_factor=None,
    stop_y_dist=None,
    rolling_n=5,
):
    """
    Finds the first gap in the words list.
    :param words: list of words
    :param init_word_height: initial word height
    :param start_i: starting index
    :param end_i: ending index
    :param step: step size
    :param line_spacing: line spacing. That is, if 2 words differ in y-value more than line_spacing * word_height,
        then that is considered a gap.
    :param stop_y_factor: if we drift by a total of more than stop_y_factor * word_height, we stop.
        This is intended to eliminate paragraphs. This parameter is preferred over stop_y_dist.
    :param stop_y_dist: if we drift by a total of more than stop_y_dist, we stop. This is intended to
        eliminate paragraphs.
    :param rolling_n: a rolling estimate is used to estimate the word height, intended to account for differences between
        table word height and caption word height. Higher = more weight to initial estimate.
    :return int: the index of the first word which has been separated by a gap.
    Returns end_i if no gap is found.
    If number of lines exceeds maxlines, then None is returned.
    """

    if not (0 <= start_i < len(words)):
        return end_i

    yorig = (words[start_i][1] + words[start_i][3]) / 2
    yprev = yorig
    if stop_y_dist is None:
        if stop_y_factor is None:
            stop_y_factor = 12.5

    # case 1: dist is None, factor is None (default) --> change to case 2
    # case 2: dist is None, factor is not None --> factor used
    # case 3: dist is not None, factor is None --> dist used
    # case 4: dist is not None, factor is not None --> factor preferred.

    # keep a rolling word height.
    # this is because the table's median word height might not be the paragraph's or the caption's.

    # rolling_n = estimate_strength
    # # initialize rolling_n; assume that init_word_height (table's word height) is somewhat close
    word_height = init_word_height

    for i in range(start_i + step, end_i, step):
        _, ymin, _, ymax, _ = words[i]
        yavg = (ymin + ymax) / 2
        height = ymax - ymin
        word_height = (rolling_n - 1) / rolling_n * word_height + height / rolling_n
        rolling_n += 1
        if yprev is not None and abs(yavg - yprev) > line_spacing * word_height:
            return i
        # need to update stop_y_dist based on new and improved word height
        stop_dist = (
            stop_y_factor * word_height if stop_y_factor is not None else stop_y_dist
        )
        if abs(yavg - yorig) > stop_dist:
            return None
        yprev = yavg
    return end_i


# rewrite time


def _find_captions(
    ct: CroppedTable,
    margin=None,
    line_spacing=2.5,
    stop_y_factor_above=10,
    stop_y_factor_below=10,
) -> tuple[str, str]:
    """
    Find captions in a table.

    :param stop_y_factor_above: if the top caption gets taller than stop_y_factor_above * caption_word_height, we stop. This is intended to eliminate paragraphs.
    :param stop_y_factor_below: if the bottom caption gets taller than stop_y_factor_below * caption_word_height, we stop. This is intended to eliminate paragraphs.
    """
    # if max_gap_space is None:
    # word_height = ct.predicted_word_height()
    # max_gap_space = ct.predicted_word_height() * 2.5
    # maximum_supported_rows=5
    if margin is None:
        margin = (50, 50, 0, 50)  # d_xmin, d_ymin, d_xmax, d_ymax to look for captions
    # search_rect = Rect(ct.rect.xmin - margin[0], ct.rect.ymin - margin[1], ct.rect.xmax + margin[2], ct.rect.ymax + margin[3])

    midpoint = (ct.rect.ymax + ct.rect.ymin) / 2

    left_edge = ct.rect.xmin - margin[0]  # 0
    right_edge = ct.rect.xmax + margin[2]  # ct.page.width
    search_rect_above = Rect(
        (left_edge, ct.rect.ymin - margin[1], right_edge, midpoint)
    )
    search_rect_below = Rect(
        (left_edge, midpoint, right_edge, ct.rect.ymax + margin[3])
    )

    words = list(ct.page.get_positions_and_text())
    # this time, aim for simplicity.
    # look for the text that is closest to the table bbox

    table_minimum_idx = len(words)
    table_maximum_idx = 0
    for i, w in enumerate(words):
        w_bbox = Rect(w[:4])
        if w_bbox.is_intersecting(ct.bbox):
            # this is considered to be in the table
            table_minimum_idx = min(table_minimum_idx, i)
            table_maximum_idx = max(table_maximum_idx, i)

    # candidates:
    # first, prefer our neighbors in reading order
    candidate_above = None
    candidate_below = None
    above_heights = []
    below_heights = []
    _candidate_y = None

    # place the immediate predecessor
    cand = table_minimum_idx - 1
    if 0 <= cand < len(words):
        wbox = Rect(words[cand][:4])
        y = (wbox.ymin + wbox.ymax) / 2
        if wbox.is_intersecting(search_rect_above):
            candidate_above = cand
            above_heights.append(wbox.ymax - wbox.ymin)
            _candidate_y = y
        elif wbox.is_intersecting(search_rect_below):
            candidate_below = cand
            below_heights.append(wbox.ymax - wbox.ymin)
            _candidate_y = y

    # place the immediate successor
    cand = table_maximum_idx + 1
    if 0 <= cand < len(words):
        wbox = Rect(words[cand][:4])
        y = (wbox.ymin + wbox.ymax) / 2
        if wbox.is_intersecting(search_rect_above):
            if candidate_above is None or abs(_candidate_y - ct.rect.ymin) > abs(
                y - ct.rect.ymin
            ):
                # if the other cand exists, prefer the one that is closer to the table
                candidate_above = cand
            above_heights.append(wbox.ymax - wbox.ymin)

        elif wbox.is_intersecting(search_rect_below):
            if candidate_below is None or abs(_candidate_y - ct.rect.ymax) > abs(
                y - ct.rect.ymax
            ):
                # if the other cand exists, prefer the one that is closer to the table
                candidate_below = cand
            below_heights.append(wbox.ymax - wbox.ymin)

    if not candidate_above:
        # resort to looking at bbox
        # strict: do not accidentally take from other column, so the x must be above the table's
        search_rect_above_strict = Rect(
            (
                ct.rect.xmin - margin[0],
                ct.rect.ymin - margin[1],
                ct.rect.xmax + margin[2],
                midpoint,
            )
        )
        best_proximal = None
        best_proximal_y = None
        for i, w in enumerate(words):
            wbox = Rect(w[:4])
            y = (wbox.ymin + wbox.ymax) / 2
            if wbox.is_intersecting(
                search_rect_above_strict
            ) and not wbox.is_intersecting(ct.bbox):
                above_heights.append(wbox.ymax - wbox.ymin)
                if best_proximal is None or abs(best_proximal_y - ct.rect.ymin) > abs(
                    y - ct.rect.ymin
                ):
                    best_proximal = i
                    best_proximal_y = y

        # now, advance best_proximal until we find a gap
        # we need to do this because of the x: it might be right of the table

        if best_proximal is not None:
            candidate_above = best_proximal

    if not candidate_below:
        # resort to looking at bbox
        # strict: do not accidentally take from other column, so the x must be above the table's
        search_rect_below_strict = Rect(
            (
                ct.rect.xmin - margin[0],
                midpoint,
                ct.rect.xmax + margin[2],
                ct.rect.ymax + margin[3],
            )
        )
        best_proximal = None
        best_proximal_y = None
        for i, w in enumerate(words):
            wbox = Rect(w[:4])
            y = (wbox.ymin + wbox.ymax) / 2
            if wbox.is_intersecting(
                search_rect_below_strict
            ) and not wbox.is_intersecting(ct.bbox):
                below_heights.append(wbox.ymax - wbox.ymin)
                if best_proximal is None or abs(best_proximal_y - ct.rect.ymax) > abs(
                    y - ct.rect.ymax
                ):
                    best_proximal = i
                    best_proximal_y = y
        # now, retreat first_proximal until we find a gap
        # we need to do this because of the x: it might be left of the table
        if best_proximal is not None:
            candidate_below = best_proximal

    captions = []
    # candidate above/below
    for cand in [candidate_above, candidate_below]:
        if cand is None:
            captions.append("")
            continue
        first = last = cand
        caption = ""
        # prior
        stop_i = -1
        if table_maximum_idx < first:
            stop_i = table_maximum_idx

        # estimate word height
        # height_estimate = word_height
        if cand == candidate_above:
            assert len(above_heights), f"logic error"
            height_estimate = np.mean(above_heights)
            height_estimate_n = len(above_heights)
        else:
            assert len(below_heights), f"logic error"
            height_estimate = np.mean(below_heights)
            height_estimate_n = len(below_heights)
        prior = _find_gap(
            words,
            height_estimate,
            first,
            stop_i,
            -1,
            line_spacing=line_spacing,
            stop_y_factor=stop_y_factor_above,
            rolling_n=height_estimate_n,
        )
        if prior is not None:
            # post
            stop_i = len(words)
            if last < table_minimum_idx:
                stop_i = table_minimum_idx
            post = _find_gap(
                words,
                height_estimate,
                last,
                stop_i,
                line_spacing=line_spacing,
                stop_y_factor=stop_y_factor_below,
                rolling_n=height_estimate_n,
            )
            if post is not None:
                caption = " ".join([words[i][4] for i in range(prior + 1, post)])
        captions.append(caption)

    return (captions[0], captions[1])  # [caption_above, caption_below]


def _detect_caption_with_mu(
    table_bbox: Tuple[float, float, float, float],
    block: Tuple[float, float, float, float, str],
    max_abs_dist: float = 2.5,
) -> Tuple[str, str]:
    x1, y1, x2, y2 = block[:4]
    text = block[4]

    # Block in PyMupdf can consist of multiple lines of text
    n_lines = text.count("\n") + 1

    normalized_dist = 1000
    top_caption, bottom_caption = "", ""

    # Take care of captions above the table
    if y2 < table_bbox[1]:  # block in question is above the table
        # Normalized distance = how many word "lines" this current sentence is from the table
        normalized_dist = (y2 - table_bbox[1]) / ((y2 - y1) / n_lines)
        if abs(normalized_dist) < max_abs_dist:
            top_caption = block[4]

    # Take care of captions below the table
    elif y1 > table_bbox[3]:  # block in question is below the table
        normalized_dist = (y1 - table_bbox[3]) / ((y2 - y1) / n_lines)
        if abs(normalized_dist) < max_abs_dist:
            bottom_caption = block[4]
    return top_caption, bottom_caption


# Extract captions using PyMuPDF, assumes we have table bbox


def _find_caption_with_mu(ct: CroppedTable, **kwargs):
    # import gmft_pymupdf
    import pymupdf

    page = ct.page.page  # type: pymupdf.TextPage
    blocks = page.get_text_blocks()

    top_captions, bottom_captions = [], []
    for block in blocks:
        top_cap, bottom_cap = _detect_caption_with_mu(table_bbox=ct.bbox, block=block)
        top_captions.append(top_cap)
        bottom_captions.append(bottom_cap)

    top_captions = "\n".join([c for c in top_captions if c])  # clear out empty captions
    bottom_captions = "\n".join([c for c in bottom_captions if c])

    whitespace_re = re.compile(r"\s*[\u202f\u2002\u2009\u00A0]\s*")  #  \u2002 \u2009
    top_captions = re.sub(whitespace_re, " ", top_captions).replace("\n", "")
    bottom_captions = re.sub(whitespace_re, " ", bottom_captions).replace("\n", "")
    return (
        top_captions,
        bottom_captions,
    )  # ('\n'.join(top_captions), '\n'.join(bottom_captions))
