from __future__ import annotations  # 3.7

from typing import Generator

from gmft.base import Rect
from gmft.pdf_bindings.base import BasePDFDocument, BasePage, _infer_line_breaks

from PIL.Image import Image as PILImage
import io

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gmft.detectors.base import CroppedTable

import pypdfium2 as pdfium
from pdftext.extraction import dictionary_output

# monkey patch a method
# from pdftext import extraction
# def _fixed_load_pdf(pdf, flatten_pdf):
#     if isinstance(pdf, pdfium.PdfDocument):
#         return pdf
#     pdf = pdfium.PdfDocument(pdf)

#     if flatten_pdf:
#         pdf.init_forms()

#     return pdf
# extraction._load_pdf = _fixed_load_pdf


class PDFTextPage(BasePage):
    """
    Note: This follows PIL's convention of (0, 0) being top left.
    Therefore, beware: y0 and y1 are flipped from PyPDFium2's convention.
    """

    def __init__(
        self, parent: PDFTextDocument, page: pdfium.PdfPage, filename: str, page_no: int
    ):
        self.page = page
        self.parent = parent
        self.filename = filename
        self.width = self.page.get_width()
        self.height = self.page.get_height()
        self._positions_and_text = []  # cache results, because this appears to be slow
        self._positions_and_text_and_breaks = []
        super().__init__(page_no)

    def get_positions_and_text(
        self,
    ) -> Generator[tuple[float, float, float, float, str], None, None]:
        """
        A generator of text and positions.
        The tuple is (x0, y0, x1, y1, "string")

        Warning: PyPDFium2Page caches the results of this method.
        """
        for x0, y0, x1, y1, text, _, _, _ in self._get_positions_and_text_and_breaks():
            yield x0, y0, x1, y1, text

    def get_filename(self) -> str:
        return self.filename

    def get_image(self, dpi: int = None, rect: Rect = None) -> PILImage:
        if dpi is None:
            dpi = 72
        scale_factor = dpi / 72
        if rect is None:
            bitmap = self.page.render(scale=scale_factor)
        else:
            # crop is "amount to cut off" from each side
            # left, bottom, right, top
            # crop = (rect.bbox[0], rect.bbox[1], self.page.get_width() - rect.bbox[0], self.page.get_height() - rect.bbox[1])
            xmin, ymin, xmax, ymax = rect.bbox
            # also remember that the origin is at the bottom left
            crop = (xmin, self.height - ymax, self.width - xmax, ymin)
            bitmap = self.page.render(scale=scale_factor, crop=crop)
        return bitmap.to_pil()

    def close(self):
        self.page.close()
        self.page = None

    # def __del__(self):
    #     if self.page is not None:
    #         self.close()

    def close_document(self):
        # if self.page.parent:
        # self.page.parent.close()
        # self.page = None
        self.parent.close()

    def _get_positions_and_text_and_breaks(self):
        """
        [Experimental] This is a generator that returns the positions and text of the page, as well as the breaks.
        """
        # cache, since it is slow
        if self._positions_and_text_and_breaks:
            for item in self._positions_and_text_and_breaks:
                yield item
            return

        # generate
        captured = []
        # disable_links necessary to not close the document
        dict_page = dictionary_output(
            self.parent.pdfbytes, page_range=[self.page_number], disable_links=True
        )[0]
        for b, block in enumerate(dict_page["blocks"]):
            for l, line in enumerate(block["lines"]):
                for s, span in enumerate(line["spans"]):
                    bbox = span["bbox"]
                    out = (
                        bbox[0],
                        bbox[1],
                        bbox[2],
                        bbox[3],
                        span["text"].replace("\n", "").strip(),
                        b,
                        l,
                        s,
                    )
                    captured.append(out)
                    yield out
        self._positions_and_text_and_breaks = captured


class PDFTextDocument(BasePDFDocument):
    """
    Wraps a pdfium.PdfDocument object. Note that the memory lifecycle is tightly coupled to the pdfium.PdfDocument object. When this object is destroyed,
    the underlying document is also destroyed.
    """

    def __init__(self, filename: str):
        with open(filename, "rb") as f:
            pdfbytes = f.read()
        self.pdfbytes = io.BytesIO(pdfbytes)
        self._doc = pdfium.PdfDocument(pdfbytes)
        self.filename = filename

    def get_page(self, n: int) -> BasePage:
        """
        Get 0-indexed page
        """
        return PDFTextPage(self, self._doc[n], self.filename, n)

    def get_filename(self) -> str:
        return self.filename

    def __len__(self) -> int:
        return len(self._doc)

    def close(self):
        """
        Close the document
        """
        if self._doc is not None:
            self._doc.close()
        self._doc = None

    # def __del__(self):
    #     if self._doc is not None:
    #         self.close()
