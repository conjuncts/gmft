import json
import pytest

import matplotlib

from gmft.table_function import TATRFormattedTable
matplotlib.use('Agg')

from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.table_detection import TableDetector, TableDetectorConfig
from gmft import AutoTableDetector, AutoTableFormatter

# from gmft_pymupdf import PyMuPDFDocument


@pytest.fixture(scope="session")
def detector():
    yield TableDetector()

@pytest.fixture(scope="session")
def formatter():
    yield AutoTableFormatter()

@pytest.fixture(scope="session")
def doc_pubt():
    doc = PyPDFium2Document("test/samples/tatr.pdf")
    yield doc
    # cleanup
    doc.close()


@pytest.fixture(scope="session")
def doc_tiny():
    doc = PyPDFium2Document("test/samples/tiny.pdf")
    yield doc
    # cleanup
    doc.close()
    
@pytest.fixture(scope="session")
def docs_bulk():
    docs = []
    for i in range(1, 9):
        doc = PyPDFium2Document(f"test/samples/{i}.pdf")
        # doc = PyMuPDFDocument(f"test/samples/{i}.pdf")
        docs.append(doc)

    yield docs
    # cleanup
    for doc in docs:
        doc.close()


_num_tables = {
    1: 10,
    2: 4,
    3: 4,
    4: 2, 
    5: 2, 
    6: 3, 
    7: 3, 
    8: 2,
}

REDETECT_TABLES=False
def get_tables_for_pdf(docs_bulk, detector: AutoTableDetector, formatter: AutoTableFormatter, n, REDETECT_TABLES=REDETECT_TABLES):
    print("Making tables for pdf", n)
    doc = docs_bulk[n-1]
    # for i, doc in enumerate(docs_bulk):
    
    config = TableDetectorConfig()
    config.detector_base_threshold = 0.9
    tables = []
    if REDETECT_TABLES:
        cropped = []
        for page in doc:
            cropped += detector.extract(page)
        for crop in cropped:
            try:
                tables.append(formatter.extract(crop)) # , margin='auto', padding=None))
            except Exception as e:
                # print(e)
                raise e
                # pass
                # tables.append(None)
    else:
        for j in range(_num_tables[n]):
            with open(f"test/outputs/bulk/pdf{n}_t{j}.info", "r") as f:
                as_dict = json.load(f)
                page_no = as_dict["page_no"]
                page = doc[page_no]
                tables.append(TATRFormattedTable.from_dict(as_dict, page))
    return tables

@pytest.fixture(scope="session")
def pdf1_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 1)
@pytest.fixture(scope="session")
def pdf2_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 2)
@pytest.fixture(scope="session")
def pdf3_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 3)
@pytest.fixture(scope="session")
def pdf4_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 4)
@pytest.fixture(scope="session")
def pdf5_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 5)
@pytest.fixture(scope="session")
def pdf6_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 6)
@pytest.fixture(scope="session")
def pdf7_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 7)
@pytest.fixture(scope="session")
def pdf8_tables(docs_bulk, detector, formatter):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, 8)
