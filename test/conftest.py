import pytest

from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import TableDetector
from gmft import AutoTableFormatter


@pytest.fixture(scope="session")
def detector():
    yield TableDetector()

@pytest.fixture(scope="session")
def formatter():
    yield AutoTableFormatter()

@pytest.fixture(scope="session")
def docs_bulk():
    docs = []
    for i in range(1, 9):
        doc = PyPDFium2Document(f"test/samples/{i}.pdf")
        docs.append(doc)

    yield docs
    # cleanup
    for doc in docs:
        doc.close()