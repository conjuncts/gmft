from typing import List, Optional, TYPE_CHECKING

from gmft.algorithm.dividers import find_column_for_target, find_row_for_target
from gmft.core.schema import WordMetadata

if TYPE_CHECKING:
    from gmft.detectors.base import CroppedTable


class WordsList:
    """
    Store a table's words.

    [Experimental, unstable] meant for internal use only. All methods can change without warning.
    """

    def __init__(self):
        self._words: list[tuple[float, float, float, float, str]] = []
        """List of word text+bboxes."""
        self._hierarchy: List[tuple[int, int, int]] = []
        """List of (block_no, line_no, row_no) tuples for each word."""
        self._meta: List[Optional[WordMetadata]] = []
        """List of metadata dictionaries for each word."""
        self._indices: List[int] = []
        """List of indices of the words as they appear in the original PDF page."""

        self._cuts: Optional[List[tuple[float, float]]] = None
        """Each word can be assigned a row index and a column index based on cut().
        Note: this is dynamically adjusted after calls to cut() and will mutate."""

    @staticmethod
    def from_table(ct: "CroppedTable") -> "WordsList":
        instance = WordsList()

        for word in ct.text_positions(remove_table_offset=True, _extra_info=True):
            instance._words.append(word[:5])
            instance._hierarchy.append(word[5:8])
            instance._meta.append(word[8])
            instance._indices.append(word[9])

        instance._offset = ct.bbox[:2]
        return instance

    @staticmethod
    def _from_state(
        words: List[tuple[float, float, float, float, str]],
        hierarchy: List[tuple[int, int, int]],
        meta: List[Optional[WordMetadata]],
        indices: List[int],
    ) -> "WordsList":
        """
        Create a WordsList from the given state.
        """
        wl = WordsList()
        wl._words = words
        wl._hierarchy = hierarchy
        wl._meta = meta
        wl._indices = indices
        wl._cuts = None
        return wl

    def cut(
        self,
        row_dividers: List[float],
        col_dividers: List[float],
        *,
        _store_in_place=True,
    ) -> None:
        """
        Assigns row and column indices to each word based on the provided dividers.

        This will mutate the internal state of the WordsList object.
        """
        cuts = []
        for word in self.iter_words():
            x_center = (word[0] + word[2]) / 2
            y_center = (word[1] + word[3]) / 2

            col_idx = find_column_for_target(col_dividers, x_center) - 1
            row_idx = find_row_for_target(row_dividers, y_center) - 1

            cuts.append((row_idx, col_idx))

        if _store_in_place:
            self._cuts = cuts
        return cuts

    def iter_words(self, *, split_hyphens=False):
        """
        Iterate over the words in the table.

        If split_hyphens is True, yields hyphenated parts as separate words.
        """

        if split_hyphens:
            for word, meta in zip(self._words, self._meta):
                if meta and meta["is_hyphenated"]:
                    yield from meta["hyphen_parts"]
                else:
                    yield word
        else:
            yield from self._words

    def _split_hyphens(self) -> "WordsList":
        """
        Permanently split hyphenated words into their parts.
        """
        new_words = []
        new_hierarchy = []
        new_meta = []
        new_indices = []

        # hierarchy needs to be updated
        # block_idx and line_idx can match, but word_idx needs to be reassigned
        # to ensure it is unique steady increasing
        word_ctr = 0
        for word, hier, meta, idx in zip(
            self._words, self._hierarchy, self._meta, self._indices
        ):
            if hier[2] == 0:
                # reset exactly when the original word_idx resets
                word_ctr = 0

            if meta and meta["is_hyphenated"]:
                for part in meta["hyphen_parts"]:
                    new_words.append(part)
                    new_meta.append(meta)
                    new_indices.append(idx)

                    new_hierarchy.append((hier[0], hier[1], word_ctr))
                    word_ctr += 1
            else:
                new_words.append(word)
                new_meta.append(meta)
                new_indices.append(idx)

                new_hierarchy.append((hier[0], hier[1], word_ctr))
                word_ctr += 1

        return WordsList._from_state(
            words=new_words,
            hierarchy=new_hierarchy,
            meta=new_meta,
            indices=new_indices,
        )

    def _to_records(self, cuts=None) -> List[dict]:
        results = []
        if cuts is None:
            cuts = self._cuts

        for word, cut in zip(self.iter_words(), cuts):
            row_idx, col_idx = cut
            results.append(
                {
                    "xmin": word[0],
                    "ymin": word[1],
                    "xmax": word[2],
                    "ymax": word[3],
                    "text": word[4],
                    "row_idx": row_idx,
                    "col_idx": col_idx,
                }
            )
        return results
