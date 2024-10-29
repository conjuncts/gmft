import json
import pytest

import matplotlib

from gmft.table_function import TATRFormattedTable
matplotlib.use('Agg')

from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.detectors.tatr import TATRDetector, TATRDetectorConfig
from gmft.auto import AutoTableDetector, AutoTableFormatter

# from gmft_pymupdf import PyMuPDFDocument

# test legacy imports
from gmft.detectors.tatr import TATRTableDetectorConfig


@pytest.fixture(scope="session")
def detector():
    yield TATRDetector()

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
def get_tables_for_pdf(docs_bulk, detector: AutoTableDetector, formatter: AutoTableFormatter, tatr_tables, n, REDETECT_TABLES=REDETECT_TABLES):
    print("Making tables for pdf", n)
    doc = docs_bulk[n-1]
    
    config = TATRTableDetectorConfig() # purposefully use old alias
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
                raise e
    else:
        for j in range(_num_tables[n]):
            as_dict = tatr_tables[f"pdf{n}_t{j}"]
            page = doc[as_dict["page_no"]]
            tables.append(TATRFormattedTable.from_dict(as_dict, page))
    return tables

@pytest.fixture(scope="session")
def cropped_tables():
    with open("test/refs/cropped_tables.json", "r") as f:
        yield json.load(f)

@pytest.fixture(scope="session")
def tatr_tables():
    with open("test/refs/tatr_tables.json", "r") as f:
        yield json.load(f)

@pytest.fixture(scope="session")
def tatr_csvs():
    with open("test/refs/tatr_csvs.json", "r") as f:
        yield json.load(f)

@pytest.fixture(scope="session")
def ditr_tables():
    with open("test/refs/ditr_tables.json", "r") as f:
        yield json.load(f)
        
@pytest.fixture(scope="session")
def ditr_csvs():
    with open("test/refs/ditr_csvs.json", "r") as f:
        yield json.load(f)

@pytest.fixture(scope="session")
def pdf1_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 1)
@pytest.fixture(scope="session")
def pdf2_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 2)
@pytest.fixture(scope="session")
def pdf3_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 3)
@pytest.fixture(scope="session")
def pdf4_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 4)
@pytest.fixture(scope="session")
def pdf5_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 5)
@pytest.fixture(scope="session")
def pdf6_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 6)
@pytest.fixture(scope="session")
def pdf7_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 7)
@pytest.fixture(scope="session")
def pdf8_tables(docs_bulk, detector, formatter, tatr_tables):
    yield get_tables_for_pdf(docs_bulk, detector, formatter, tatr_tables, 8)
