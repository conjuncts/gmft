
# PyMuPDF bindings
from typing import Generator
import PIL
import pymupdf

from PIL.Image import Image as PILImage

from gmft.common import Rect
from gmft.pdf_bindings import BasePage, BasePDFDocument


def pixmap_to_PIL(pixmap: pymupdf.Pixmap) -> PILImage:
    """
    Convert a MuPDF pixmap to a PIL Image.
    :param pixmap: MuPDF pixmap
    :return: PIL Image
    """
    img = PIL.Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    return img

class PyMuPDFPage(BasePage):
    
    def __init__(self, page: pymupdf.Page):
        self.page = page
        super().__init__(page.number)
    
    def get_positions_and_text(self) -> Generator[tuple[float, float, float, float, str], None, None]:
        for word in self.page.get_text("words"):
            yield word[:5]
    
    def get_filename(self) -> str:
        return self.page.parent.name
    
    def get_image(self, dpi: int=None, rect: Rect=None) -> PILImage:
        
        img = pixmap_to_PIL(self.page.get_pixmap(dpi=dpi, clip=None if rect is None else rect.bbox))
        return img

class PyMuPDFDocument(BasePDFDocument):
    
    def __init__(self, filename: str):
        self.doc = pymupdf.open(filename)
    
    def get_page(self, n: int) -> BasePage:
        return PyMuPDFPage(self.doc[n])
    
    def __len__(self) -> int:
        return len(self.doc)