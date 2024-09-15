from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.table_detection import CroppedTable
from gmft import AutoTableDetector


default_detector = None
def ingest_pdf(pdf_path) -> list[CroppedTable]:
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