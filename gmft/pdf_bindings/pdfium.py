from __future__ import annotations  # 3.7

# PyPDFium2 bindings
from typing import Generator, List, Tuple
import pypdfium2 as pdfium

from gmft.base import Rect
from gmft.core.exception import DocumentClosedException
from gmft.core.schema import FineTextBbox, TextBboxMetadata
from gmft.pdf_bindings.base import BasePDFDocument, BasePage, _infer_line_breaks

from PIL.Image import Image as PILImage


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gmft.formatters.base import CroppedTable


class PyPDFium2Page(BasePage):
    """
    Note: This follows PIL's convention of (0, 0) being top left.
    Therefore, beware: y0 and y1 are flipped from PyPDFium2's convention.
    """

    def __init__(
        self,
        page: pdfium.PdfPage,
        filename: str,
        page_no: int,
        *,
        parent: "PyPDFium2Document" = None,
    ):
        self.parent = parent
        self.page = page
        self.filename = filename
        self.width = page.get_width()
        self.height = page.get_height()
        self._positions_and_text_and_breaks = None
        super().__init__(page_no)

    def get_positions_and_text(
        self,
    ) -> Generator[Tuple[float, float, float, float, str], None, None]:
        """
        A generator of text and positions.
        The tuple is (x0, y0, x1, y1, "string")

        Warning: PyPDFium2Page caches the results of this method.
        """
        # {0: '?', 1: 'text', 2: 'path', 3: 'image', 4: 'shading', 5: 'form'}

        # Problem: num_rect is not finely grained enough, as it tends to clump multiple words together
        # For instance, the following code would NOT work:

        # textpage = self.page.get_textpage()
        # num_rects = textpage.count_rects()
        # for i in range(num_rects):
        #     rect = textpage.get_rect(i) # left, bottom, right, top
        #     text = textpage.get_text_bounded(*rect)
        #     adjusted = (rect[0], self.height - rect[3], rect[2], self.height - rect[1])
        #     yield *adjusted, text

        if self._positions_and_text_and_breaks is None:
            self._initialize_word_bboxes()
            assert self._positions_and_text_and_breaks is not None

        for tup in self._positions_and_text_and_breaks:
            yield tup[:5]

    def get_filename(self) -> str:
        return self.filename

    def get_image(self, dpi: int = None, rect: Rect = None) -> PILImage:
        if self._is_closed():
            raise DocumentClosedException("Document was already closed")
        if dpi is None:
            dpi = 72
        scale_factor = dpi / 72
        if rect is None:
            bitmap = self.page.render(scale=scale_factor)
        else:
            # crop is "amount to cut off" from each side
            # left, bottom, right, top
            xmin, ymin, xmax, ymax = rect.bbox
            # also remember that the origin is at the bottom left
            crop = (xmin, self.height - ymax, self.width - xmax, ymin)
            bitmap = self.page.render(scale=scale_factor, crop=crop)
        return bitmap.to_pil()

    def close(self):
        """
        Not recommended: use close_document instead.
        """
        self.page.close()
        self.page = None

    def close_document(self):
        if self.parent:
            self.parent.close()
        elif self.page.parent:
            self.page.parent.close()
        self.page = None

    def _is_closed(self):
        """
        Check if the page is closed.
        """
        return self.page is None or self.parent._is_closed()

    def _initialize_word_bboxes(self):
        if self._positions_and_text_and_breaks is not None:
            return  # nothing to do

        if self._is_closed():
            raise DocumentClosedException("Document was already closed")

        result = []
        text_page = self.page.get_textpage()

        # Directionality for rudimentary hyphenation detection
        current_direction = {"ltr": 0, "unk": 0}

        # Aggregate chars into words
        current_word = ""
        current_bbox = None

        current_hyphen_parts = []

        def _push_and_restart_word():
            nonlocal \
                current_word, \
                current_bbox, \
                current_hyphen_parts, \
                result, \
                current_direction
            components = [*current_hyphen_parts, (*current_bbox, current_word)]

            # transform pypdfium coords to standard
            for i, comp in enumerate(components):
                components[i] = (
                    comp[0],
                    self.height - comp[3],
                    comp[2],
                    self.height - comp[1],
                    comp[4],
                )

            # get overall bbox
            current_bbox = (
                min(x[0] for x in components),
                min(x[1] for x in components),
                max(x[2] for x in components),
                max(x[3] for x in components),
            )
            current_word = "".join(x[4] for x in components)

            # produce metadata
            metadata = {
                "direction": "ltr" if not current_direction["unk"] else None,
                "is_hyphenated": bool(current_hyphen_parts),
                "hyphen_parts": None,
            }
            if len(components) > 1:
                metadata["hyphen_parts"] = components[1:]

            result.append((*current_bbox, current_word, metadata))
            # reset
            current_word = ""
            current_bbox = None
            current_direction = {"ltr": 0, "unk": 0}
            current_hyphen_parts = []

        for index in range(text_page.count_chars()):
            bbox = text_page.get_charbox(index)
            char = text_page.get_text_range(index, 1)
            # if is whitespace
            if char.isspace():
                if current_word:
                    _push_and_restart_word()
            else:
                if current_bbox is None:
                    current_word += char
                    current_bbox = bbox
                else:
                    if bbox[0] < current_bbox[0]:
                        # candidate for hyphenation (effectively a carriage return)
                        if (
                            current_direction["ltr"] >= 3
                            and current_direction["unk"] == 0
                            and not current_word[-1].isalnum()
                        ):
                            # is LTR and is hyphen-like (not alphanumeric)
                            current_hyphen_parts.append((*current_bbox, current_word))
                            current_word = char
                            current_bbox = bbox
                            continue

                    # update standard LTR reading
                    if current_bbox[0] <= bbox[0] and current_bbox[2] <= bbox[2]:
                        current_direction["ltr"] += 1
                    else:
                        current_direction["unk"] += 1

                    # must update current after hyphenation checks
                    current_word += char
                    # for the bbox, take the union
                    current_bbox = (
                        min(current_bbox[0], bbox[0]),
                        min(current_bbox[1], bbox[1]),
                        max(current_bbox[2], bbox[2]),
                        max(current_bbox[3], bbox[3]),
                    )
        # Add the last word
        if current_word:
            _push_and_restart_word()

        no_meta = [x[:5] for x in result]
        meta = [x[5] for x in result]
        words = list(_infer_line_breaks(no_meta))
        self._positions_and_text_and_breaks = [(*a, b) for a, b in zip(words, meta)]

    def _get_positions_and_text_and_breaks(self):
        """
        [Experimental] This is a generator that returns the positions and text of the page, as well as the breaks.
        """
        # cache, since it is slow
        if self._positions_and_text_and_breaks is None:
            self._initialize_word_bboxes()

        for item in self._positions_and_text_and_breaks:
            yield item[:8]

    def _get_text_with_metadata(self) -> List[FineTextBbox]:
        if self._positions_and_text_and_breaks is None:
            self._initialize_word_bboxes()
        return self._positions_and_text_and_breaks


class PyPDFium2Document(BasePDFDocument):
    """
    Wraps a pdfium.PdfDocument object.
    Note that you (the user) are responsible for calling doc.close() once you are done,
    otherwise the document will remain open and consume resources.
    """

    def __init__(self, filename: str):
        self._doc = pdfium.PdfDocument(filename)
        self.filename = filename

    def get_page(self, n: int) -> BasePage:
        """
        Get 0-indexed page
        """
        return PyPDFium2Page(self._doc[n], self.filename, n, parent=self)

    def get_filename(self) -> str:
        return self.filename

    def __len__(self) -> int:
        if self._is_closed():
            raise DocumentClosedException("Document was already closed")
        return len(self._doc)

    def close(self):
        """
        Close the document
        """
        if self._doc is not None:
            self._doc.close()
        self._doc = None

    def _is_closed(self):
        """
        Check if the page is closed.
        """
        return self._doc is None


class PyPDFium2Utils:
    """
    Helper class for pypdfium2
    """

    @staticmethod
    def load_page_from_dict(d: dict) -> BasePage:
        """
        Helper method to load a BasePage from a serialized CroppedTable or TATRFormattedTable.
        This method reads a pdf from disk! You will need to close it manually!

        ie. `page.close_document()`
        """
        filename = d["filename"]
        page_number = d["page_no"]

        doc = PyPDFium2Document(filename)
        return doc.get_page(page_number)

    @staticmethod
    def reload(
        ct: "CroppedTable", doc=None
    ) -> Tuple["CroppedTable", "PyPDFium2Document"]:
        """
        Reloads the :class:`.CroppedTable` from disk.
        This is useful for a :class:`.CroppedTable` whose document has been closed.

        :param ct: The :class:`.CroppedTable` to reload.
        :param doc: The :class:`.PyPDFium2Document` to reload from. If None, the document is loaded from disk.
        """
        page_number = ct.page.page_number

        if doc is None:
            filename = ct.page.filename
            doc = PyPDFium2Document(filename)
        page = doc.get_page(page_number)

        ct.page = page
        return ct, doc  # escape analysis means we need to give doc back
