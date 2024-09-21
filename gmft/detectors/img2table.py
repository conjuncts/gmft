
import copy
from dataclasses import dataclass
from typing import Generator
import img2table.document
import numpy as np
import pandas as pd

from gmft.common import Rect
from gmft.detectors.common import BaseDetector, CroppedTable
from gmft.formatters.common import FormattedTable
from gmft.pdf_bindings.common import BasePDFDocument, BasePage


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
    Wraps a BasePDFdocument in the img2table format
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
                self.ocr_df = _PdfOCR_For_I2TDoc().of(document=pdf_ocr)

        return super(PDF, self).get_table_content(tables=tables, ocr=ocr, min_confidence=min_confidence)
    
    @property
    def bytes(self):
        raise NotImplementedError("gmft circumvents this img2table method.")
    
    @property
    def src(self):
        return self.get_filename()



class Img2TablePage(img2table.document.PDF):
    """
    Wraps a BasePage as a singleton document in the img2table format, 
    because detectors work on a page level.
    """
    
    _basepage: BasePage = None
    _image: np.ndarray = None # of the single page
    ocr_df = None
    
    def __init__(self, page: BasePage):
        self._basepage = page
    
    @property
    def images(self) -> list[np.ndarray]:
        if self._image is not None:
            return [self._image]
        
        
        img = self._basepage.get_image(dpi=200) # img2table appears to expect 200 dpi
        img = np.array(img)
            
        # per img2table, handle rotation if needed
        if self.detect_rotation:
            final, self._rotated = img2table.document.base.rotation.fix_rotation_image(img=img)
        else:
            final, self._rotated = img, False
        self._image = final
        return [final]
    
    def get_table_content(self, tables: dict[int, list[Table]], ocr: OCRInstance,
                          min_confidence: int) -> dict[int, list[ExtractedTable]]:
        if not self._rotated and self.pdf_text_extraction:
            # Get pages where tables have been detected
            table_pages = [self.pages[k] if self.pages else k for k, v in tables.items() if len(v) > 0]
            # images = [self.images[k] for k, v in tables.items() if len(v) > 0]

            if table_pages:
                
                
                # Try to get OCRDataframe from PDF
                # this is necessary to use locations instead of bytes
                self.ocr_df = _PdfOCR_For_I2TPage().of(document=self)

        return super(PDF, self).get_table_content(tables=tables, ocr=ocr, min_confidence=min_confidence)
    
    @property
    def bytes(self):
        raise NotImplementedError("gmft circumvents this img2table method.")
    
    @property
    def src(self):
        return self._basepage.get_filename()
    

class _PdfOCR_For_I2TDoc(PdfOCR):
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
                
                # this will automatically sort
                generator = page._get_positions_and_text_and_breaks()
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


class _PdfOCR_For_I2TPage(PdfOCR):
    def content(self, document: Img2TablePage) -> list[list[dict]]:
        """
        Unfortunately, blockno / lineno is an integral part of this function and is required for table detection.
        """
        list_pages = list()

        # Get image size and page dimensions
        img_height, img_width = list(document.images)[0].shape[:2]
        # page_height = (page.cropbox * page.rotation_matrix).height
        # page_width = (page.cropbox * page.rotation_matrix).width
        page = document._basepage
        page_height = page.height
        page_width = page.width

        # Extract words
        list_words = list()
        
        # need to sort by y-position, then x-position.
        if hasattr(page, "get_positions_and_text_mu"):
            stuff = list(page.get_positions_and_text_mu())
            generator = sorted(stuff, key=lambda x: (x[1], x[0]))
        else:
            # this will automatically sort
            generator = page._get_positions_and_text_and_breaks()
        for x1, y1, x2, y2, value, block_no, line_no, word_no in generator:
            # (x1, y1), (x2, y2) = fitz.Point(x1, y1) * page.rotation_matrix, fitz.Point(x2, y2) * page.rotation_matrix
            x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
            word = {
                "page": 0,
                "class": "ocrx_word",
                "id": f"word_{1}_{block_no}_{line_no}_{word_no}",
                "parent": f"line_{1}_{block_no}_{line_no}",
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
                "page": 0,
                "class": "ocr_page",
                "id": f"page_{1}",
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

class Img2TableTable(FormattedTable):
    def __init__(self, table: ExtractedTable, page: BasePage):
        self._table = table
        # call the CroppedTable super constructor
        CroppedTable.__init__(self, page=page, 
                              bbox=Rect((table.bbox.x1, table.bbox.y1, table.bbox.x2, table.bbox.y2)), 
                              confidence_score=0.9, label=0)
        
        # call the FormattedTable constructor, to handle those fields
        FormattedTable.__init__(self, cropped_table=None, df=None)
    
    def df(self, recalculate=False, config_overrides=None) -> pd.DataFrame:
        """
        Return the table as a pandas dataframe.
        """
        return self._table.df
    
    def visualize(self):
        """
        Visualize the table.
        """
        # TODO see if cell-level annotations are available
        return self.page.get_image(self.rect)
    
    def to_dict(self):
        """
        Serialize self into dict
        """
        parent = CroppedTable.to_dict(self)
        return {**parent, **{
            'type': 'img2table',
        }}
    
    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize from dict
        """
        raise NotImplementedError("This is not implemented, instead create Tables using Img2TableDetector.extract")

# @auto_init
@dataclass
class Img2TableDetectorConfig:
    implicit_rows: bool = False
    implicit_columns: bool = False
    borderless_tables: bool = False
    min_confidence: int = 50

class Img2TableDetector(BaseDetector[Img2TableDetectorConfig]):
    def __init__(self, config: Img2TableDetectorConfig=None):
        if config is None:
            config = Img2TableDetectorConfig()
        elif isinstance(config, dict):
            config = Img2TableDetectorConfig(**config)
        self.config = config
        
    def extract(self, page: BasePage, config_overrides: Img2TableDetectorConfig=None) -> list[Img2TableTable]:
        """
        Extract tables from a page.
        
        :param page: BasePage
        :param config_overrides: override the config for this call only
        :return: list of CroppedTable objects
        """
        if isinstance(page, Img2TablePage):
            i2tpage = page
        else:
            i2tpage = Img2TablePage(page)
        
        if config_overrides is not None:
            if isinstance(config_overrides, dict):
                # only update if it's a dict
                pass # TODO
            else:
                # override everything
                config = config_overrides
        else:
            config = self.config
        
        extracted_tables = i2tpage.extract_tables(ocr=None,
                                                  **config.__dict__)
            # implicit_rows=False,
            # implicit_columns=False,
            # borderless_tables=False,
            # min_confidence=50)
        
        page0tables = extracted_tables.get(0, [])
        
        result = [Img2TableTable(table=table, page=page) for table in page0tables]
        return result
        
        