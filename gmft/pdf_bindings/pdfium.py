from __future__ import annotations # 3.7

# PyPDFium2 bindings
from typing import Generator
import pypdfium2 as pdfium

from gmft.common import Rect
from gmft.pdf_bindings.common import BasePDFDocument, BasePage, _infer_line_breaks

from PIL.Image import Image as PILImage



from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gmft.table_detection import CroppedTable


class PyPDFium2Page(BasePage):
    """
    Note: This follows PIL's convention of (0, 0) being top left.
    Therefore, beware: y0 and y1 are flipped from PyPDFium2's convention. 
    """
    
    def __init__(self, page: pdfium.PdfPage, filename: str, page_no: int):
        self.page = page
        self.filename = filename
        self.width = page.get_width()
        self.height = page.get_height()
        self._positions_and_text = [] # cache results, because this appears to be slow
        self._positions_and_text_and_breaks = []
        super().__init__(page_no)
    
    def get_positions_and_text(self) -> Generator[tuple[float, float, float, float, str], None, None]:
        """
        A generator of text and positions.
        The tuple is (x0, y0, x1, y1, "string")
        
        Warning: PyPDFium2Page caches the results of this method.
        """
        # {0: '?', 1: 'text', 2: 'path', 3: 'image', 4: 'shading', 5: 'form'}
        
        # problem: num_rect is not finely grained enough, as it tends to clump multiple words together
        # textpage = self.page.get_textpage()
        # num_rects = textpage.count_rects()
        # for i in range(num_rects):
        #     rect = textpage.get_rect(i)
        #     # left, bottom, right, top
        #     text = textpage.get_text_bounded(*rect)
        #     # oof - x0 = left, y0 = height - top, x1 = right, y1 = height - bottom
        #     adjusted = (rect[0], self.height - rect[3], rect[2], self.height - rect[1])
        #     yield *adjusted, text
        
        # this is a bit more fine-grained
        
        # cache results, because this appears to be slow
        # from the superior data, pilfer what we need
        if self._positions_and_text_and_breaks:
            for x0, x1, y0, y1, text, _, _, _ in self._positions_and_text_and_breaks:
                yield x0, y0, x1, y1, text
            return
        
        if self._positions_and_text:
            for item in self._positions_and_text:
                yield item
            return
        
        result = []
        text_page = self.page.get_textpage()
        
        # "char" seems to not actually be a char, but a string-like token
        # for index in range(text_page.count_chars()):
        #     bbox = text_page.get_charbox(index)
        #     char = text_page.get_text_range(index, 1)
        #     yield *bbox, char
        
        # Aggregate chars into words
        current_word = ""
        current_bbox = None
        for index in range(text_page.count_chars()):
            bbox = text_page.get_charbox(index)
            char = text_page.get_text_range(index, 1)
            # if is whitespace
            if char.isspace():
                if current_word:
                    # perform negation
                    current_bbox = (current_bbox[0], self.height - current_bbox[3], 
                                    current_bbox[2], self.height - current_bbox[1])
                    result.append((*current_bbox, current_word)) # cache, because it is slow
                    yield *current_bbox, current_word
                    current_word = ""
                    current_bbox = None
            else:
                current_word += char
                if current_bbox is None:
                    current_bbox = bbox
                else:
                    # for the bbox, simply get the min/max
                    current_bbox = (min(current_bbox[0], bbox[0]), 
                                    min(current_bbox[1], bbox[1]), 
                                    max(current_bbox[2], bbox[2]), 
                                    max(current_bbox[3], bbox[3]))
        # Add the last word
        if current_word:
            current_bbox = (current_bbox[0], self.height - current_bbox[3], 
                            current_bbox[2], self.height - current_bbox[1])
            result.append((*current_bbox, current_word))
            yield *current_bbox, current_word
        
        self._positions_and_text = result
    
    def get_filename(self) -> str:
        return self.filename
    
    def get_image(self, dpi: int=None, rect: Rect=None) -> PILImage:
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
        if self.page.parent:
            self.page.parent.close()
        self.page = None
    
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
        words = list(_infer_line_breaks(self.get_positions_and_text()))
        self._positions_and_text_and_breaks = words
        for item in words:
            yield item
        

class PyPDFium2Document(BasePDFDocument):
    """
    Wraps a pdfium.PdfDocument object. Note that the memory lifecycle is tightly coupled to the pdfium.PdfDocument object. When this object is destroyed, 
    the underlying document is also destroyed.
    """
    
    def __init__(self, filename: str):
        self._doc = pdfium.PdfDocument(filename)
        self.filename = filename
    
    def get_page(self, n: int) -> BasePage:
        """
        Get 0-indexed page
        """
        return PyPDFium2Page(self._doc[n], self.filename, n)
    
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
        filename = d['filename']
        page_number = d['page_no']
        
        doc = PyPDFium2Document(filename)
        return doc.get_page(page_number)
    
    @staticmethod
    def reload(ct: 'CroppedTable', doc=None) -> tuple['CroppedTable', 'PyPDFium2Document']:
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
        return ct, doc # escape analysis means we need to give doc back
        
