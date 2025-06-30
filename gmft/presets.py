from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.detectors.base import CroppedTable
from gmft.auto import AutoTableDetector


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
        # Possible to insert a text regex before extraction to filter out unwanted text
        tables += default_detector.extract(page)
    return tables, doc
