import pytest

from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import TableDetector
from gmft.table_function import AutoTableFormatter


@pytest.fixture
def detector():
    return TableDetector()

@pytest.fixture
def formatter():
    return AutoTableFormatter()

@pytest.fixture
def docs_bulk():
    docs = []
    for i in range(1, 9):
        doc = PyPDFium2Document(f"test/samples/{i}.pdf")
        docs.append(doc)

    yield docs
    # cleanup
    for doc in docs:
        doc.close()