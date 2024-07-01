
# PyPDFium2 bindings
from typing import Generator
import pypdfium2 as pdfium

from gmft.common import Rect
from gmft.pdf_bindings.common import BasePDFDocument, BasePage

from PIL.Image import Image as PILImage


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
        super().__init__(page_no)
    
    def get_positions_and_text(self) -> Generator[tuple[float, float, float, float, str], None, None]:
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
        text_page = self.page.get_textpage()
        
        # "char" seems to not actually be a char, but a string-like token
        # for index in range(text_page.count_chars()):
        #     bbox = text_page.get_charbox(index)
        #     char = text_page.get_text_range(index, 1)
        #     yield *bbox, char
        
        # Aggregate chars into words
        current_word = ""
        current_bbox = None
        # text_bboxes = []
        for index in range(text_page.count_chars()):
            bbox = text_page.get_charbox(index)
            char = text_page.get_text_range(index, 1)
            # if is whitespace
            if char.isspace():
                if current_word:
                    # text_bboxes.append((current_word, current_bbox))
                    # perform negation
                    current_bbox = (current_bbox[0], self.height - current_bbox[3], 
                                    current_bbox[2], self.height - current_bbox[1])
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
            # text_bboxes.append((current_word, current_bbox))
            yield *current_bbox, current_word
        
        # Clean up
    
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
    
    def __del__(self):
        if self.page is not None:
            self.close()
    
    def close_document(self):
        if self.page.parent:
            self.page.parent.close()
        self.page = None

class PyPDFium2Document(BasePDFDocument):
    
    def __init__(self, filename: str):
        self.doc = pdfium.PdfDocument(filename)
        self.filename = filename
    
    def get_page(self, n: int) -> BasePage:
        return PyPDFium2Page(self.doc[n], self.filename, n)
    
    def __len__(self) -> int:
        return len(self.doc)
    
    def close(self):
        """
        Close the document
        """
        self.doc.close()
        self.doc = None

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
    def reload(ct: 'CroppedTable') -> 'CroppedTable':
        """
        Reloads the :class:`~gmft.CroppedTable` from disk.
        This is useful for a :class:`~gmft.CroppedTable` whose document has been closed.
        """
        page = PyPDFium2Utils.load_page_from_dict(ct.to_dict())
        ct.page = page
        return ct
        
