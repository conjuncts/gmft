
from typing import Generator
import img2table.document
import numpy as np

from gmft.pdf_bindings.common import BasePDFDocument, BasePage, _infer_line_breaks


try:
    import img2table
except ImportError:
    raise ImportError("You need to install img2table to use this detector")

from img2table.document.base import Document
from img2table.document.pdf import PDF
from img2table.ocr.base import OCRInstance
from img2table.ocr.pdf import PdfOCR
from img2table.tables.objects.table import Table
from img2table.tables.objects.extraction import ExtractedTable

class Img2TablePDFDocument(BasePDFDocument, img2table.document.PDF):
    """
    Wraps a basePDFdocument in the img2table format
    """
    
    _underlying: BasePDFDocument = None
    _images: list[np.ndarray] = None
    ocr_df = None
    def __init__(self, doc: BasePDFDocument):
        self._underlying = doc
    
    def get_page(self, n: int) -> BasePage:
        """
        Get 0-indexed page
        """
        return self._underlying.get_page(n)
    
    def __len__(self) -> int:
        return len(self._underlying)
    
    def get_filename(self) -> str:
        return self._underlying.get_filename()
    
    def __getitem__(self, n: int) -> BasePage:
        return self._underlying[n]
    
    def __iter__(self) -> Generator[BasePage, None, None]:
        yield from self._underlying
    
    def close(self):
        return self._underlying.close()
    
    @property
    def images(self) -> list[np.ndarray]:
        if self._images is not None:
            return self._images
        
        images = []
        for page in self:
            img = page.get_image(dpi=200) # img2table appears to expect 200 dpi
            img = np.array(img)
            
            # per img2table, handle rotation if needed
            if self.detect_rotation:
                final, self._rotated = img2table.document.base.rotation.fix_rotation_image(img=img)
            else:
                final, self._rotated = img, False
            images.append(final)
        self._images = images
        return images
    
    def get_table_content(self, tables: dict[int, list[Table]], ocr: OCRInstance,
                          min_confidence: int) -> dict[int, list[ExtractedTable]]:
        if not self._rotated and self.pdf_text_extraction:
            # Get pages where tables have been detected
            table_pages = [self.pages[k] if self.pages else k for k, v in tables.items() if len(v) > 0]
            images = [self.images[k] for k, v in tables.items() if len(v) > 0]

            if table_pages:
                # Create PDF object for OCR
                # pdf_ocr = PDF(src=self.bytes,
                #               pages=table_pages,
                #               _images=images,
                #               _rotated=self._rotated)
                
                pdf_ocr = self
                # I don't think it mutates? TODO Verify
                
                # Try to get OCRDataframe from PDF
                # this is necessary to use locations instead of bytes
                self.ocr_df = _Img2TableGmftPdfOCR().of(document=pdf_ocr)

        return super(PDF, self).get_table_content(tables=tables, ocr=ocr, min_confidence=min_confidence)
    
    @property
    def bytes(self):
        raise NotImplementedError("gmft circumvents this img2table method.")
    
    @property
    def src(self):
        return self.get_filename()
    

class _Img2TableGmftPdfOCR(PdfOCR):
    def content(self, document: BasePDFDocument) -> list[list[dict]]:
        """
        Unfortunately, blockno / lineno is an integral part of this function and is required for table detection.
        """
        list_pages = list()

        # doc = fitz.Document(stream=document.bytes, filetype='pdf')
        # for idx, page_number in enumerate(document.pages):
        for idx, page in enumerate(document):
            # Get page
            # page = doc.load_page(page_id=page_number)

            # Get image size and page dimensions
            img_height, img_width = list(document.images)[idx].shape[:2]
            # page_height = (page.cropbox * page.rotation_matrix).height
            # page_width = (page.cropbox * page.rotation_matrix).width
            page_height = page.height
            page_width = page.width

            # Extract words
            list_words = list()
            
            # need to sort by y-position, then x-position.
            if hasattr(page, "get_positions_and_text_mu"):
                stuff = list(page.get_positions_and_text_mu())
                generator = sorted(stuff, key=lambda x: (x[1], x[0]))
            else:
                # raise ValueError("Currently not supported, as block_no and line_no are needed for accurate table extraction.")
                # def generator_creator():
                #     ctr = 0
                #     for x0, x1, y0, y1, text in page.get_positions_and_text():
                #         approx_line_no = y0 // 10
                #         yield x0, y0, x1, y1, text, 0, approx_line_no, ctr
                #         ctr += 1
                # stuff = list(generator_creator())
                # generator = sorted(stuff, key=lambda x: (x[1], x[0]))
                generator = _infer_line_breaks(page.get_positions_and_text())
            for x1, y1, x2, y2, value, block_no, line_no, word_no in generator: # page.get_text("words", sort=True):
                # (x1, y1), (x2, y2) = fitz.Point(x1, y1) * page.rotation_matrix, fitz.Point(x2, y2) * page.rotation_matrix
                x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
                word = {
                    "page": idx,
                    "class": "ocrx_word",
                    "id": f"word_{idx + 1}_{block_no}_{line_no}_{word_no}",
                    "parent": f"line_{idx + 1}_{block_no}_{line_no}",
                    "value": value,
                    "confidence": 99,
                    "x1": round(x1 * img_width / page_width),
                    "y1": round(y1 * img_height / page_height),
                    "x2": round(x2 * img_width / page_width),
                    "y2": round(y2 * img_height / page_height)
                }
                list_words.append(word)

            if list_words:
                # Append to list of pages
                list_pages.append(list_words)
            elif len(page.get_images()) == 0:
                # Check if page is blank
                page_item = {
                    "page": idx,
                    "class": "ocr_page",
                    "id": f"page_{idx + 1}",
                    "parent": None,
                    "value": None,
                    "confidence": None,
                    "x1": 0,
                    "y1": 0,
                    "x2": img_width,
                    "y2": img_height
                }
                list_pages.append([page_item])
            else:
                list_pages.append([])

        return list_pages


        