from gmft.pdf_bindings.common import BasePDFDocument
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.detectors.common import CroppedTable
from gmft.auto import AutoTableDetector

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gmft.formatters.tatr import TATRFormattedTable


default_detector = None
def ingest_pdf(pdf_path) -> tuple[list[CroppedTable], PyPDFium2Document]:
    """
    Default ingestion function for PDFs. 
    For finer-grained control, modify this function.
    """
    doc = PyPDFium2Document(pdf_path)
    global default_detector
    if default_detector is None:
        default_detector = AutoTableDetector()

    tables = []
    for page in doc:
        # page_text = ""
        # for text in page.get_positions_and_text():
            # page_text += text[4] + " "
        # if any([re.search(x, page_text) for x in page_keywords_re_s]):
        tables += default_detector.extract(page)
    return tables, doc

def load_tatr_formatted_table(d: dict) -> tuple['TATRFormattedTable', BasePDFDocument]:
    try:
        import gmft_pymupdf
    except ImportError:
        raise ImportError("You need to install gmft_pymupdf to use this function")
    
    from gmft.formatters.tatr import TATRFormattedTable
    doc = gmft_pymupdf.PyMuPDFDocument(d['filename'])
    page = doc[d['page_no']]

    ft = TATRFormattedTable.from_dict(d, page)
    # ft.recompute()
    return ft, doc
    
