
from typing import Generator
import img2table.document
import numpy as np

from gmft.pdf_bindings.common import BasePDFDocument, BasePage
from gmft.table_detection import CroppedTable
from gmft.detectors.img2table import _PdfOCR_For_I2TDoc
from gmft.table_function import FormattedTable, TableFormatter


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

class _Img2TableCroppedPDF(img2table.document.PDF):
    """
    Creates a pdf document whose image only encloses a cropped table, for purposes of only feeding
    the table to img2table. 
    
    So basically it is a cropped PDF.
    """
    
    _table: CroppedTable = None
    _images: list[np.ndarray] = None
    ocr_df = None
    
    def __init__(self, table: CroppedTable):
        self._table = table
        images = []
        img = self._table.image(dpi=200, margin='auto') # img2table appears to expect 200 dpi
        img = np.array(img)
            
        # per img2table, handle rotation if needed
        if self.detect_rotation:
            final, self._rotated = img2table.document.base.rotation.fix_rotation_image(img=img)
        else:
            final, self._rotated = img, False
            images.append(final)
        self._images = images
        
    
    @property
    def images(self) -> list[np.ndarray]:
        return self._images
    
    def get_table_content(self, tables: dict[int, list[Table]], ocr: OCRInstance,
                          min_confidence: int) -> dict[int, list[ExtractedTable]]:
        if not self._rotated and self.pdf_text_extraction:
            # Get pages where tables have been detected
            table_pages = [self.pages[k] if self.pages else k for k, v in tables.items() if len(v) > 0]
            # images = [self.images[k] for k, v in tables.items() if len(v) > 0]

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
                
                # this is a true hijacking of the "document" parameter
                self.ocr_df = _PdfOCR_For_I2TDoc().of(document=pdf_ocr)

        return super(PDF, self).get_table_content(tables=tables, ocr=ocr, min_confidence=min_confidence)
    
    @property
    def bytes(self):
        raise NotImplementedError("gmft circumvents this img2table method.")
    
    @property
    def src(self):
        return self.get_filename()

class Img2TableFormattedTable(FormattedTable):
    def __init__(self, table: CroppedTable, result: ExtractedTable):
        super().__init__(table, result.df)
        self._table = result

class Img2TableFormatter(TableFormatter):
    """
    DO NOT USE: this is experimental and is completely untested.
    
    
    There are 2 strategies to use img2table's formatting with another provider's detection.
    
    1. Run the img2table detector, and run the other provider's detector, and only
    process tables that are detected by both (which have a high intersection).
    
    2. Run the other provider's detector, produce cropped documents, then run these through img2table.
    
    This formatter uses strategy #2.
    """
    
    def extract(self, table: CroppedTable) -> FormattedTable:
        """
        Extract the data from the table. 
        Produces a :class:`.FormattedTable` instance, from which data can be exported in csv, html, etc.
        
        Note that this method may also return None if a table is not detected.
        """
        pdf = _Img2TableCroppedPDF(table)
        result = pdf.get_table_content(tables={0: [table]}, ocr=None, min_confidence=0)
        # pdf should just have 1 page
        tables = result[0]
        if tables:
            candidate = tables[0]
            return Img2TableFormattedTable(table, candidate)
        else:
            return None
