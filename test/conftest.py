import json
import os
import re
from typing import Generator, List
import pytest

import matplotlib

from gmft.formatters.ditr import DITRFormattedTable
from gmft.formatters.tatr import TATRFormattedTable

matplotlib.use("Agg")

from gmft.pdf_bindings.base import BasePDFDocument
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.detectors.tatr import TATRDetector, TATRDetectorConfig
from gmft.auto import AutoTableDetector, AutoTableFormatter

# from gmft_pymupdf import PyMuPDFDocument
# from gmft.pdf_bindings.pdftext import PDFTextDocument

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
    doc = PyPDFium2Document("data/pdfs/tatr.pdf")
    yield doc
    # cleanup
    doc.close()


@pytest.fixture(scope="session")
def doc_tiny():
    doc = PyPDFium2Document("data/pdfs/tiny.pdf")
    yield doc
    # cleanup
    doc.close()


@pytest.fixture(scope="session")
def docs_bulk() -> Generator[List[BasePDFDocument], None, None]:
    docs = []
    for i in range(1, 9):
        doc = PyPDFium2Document(f"data/pdfs/{i}.pdf")
        # doc = PyMuPDFDocument(f"data/pdfs/{i}.pdf")
        # doc = PDFTextDocument(f"data/pdfs/{i}.pdf")
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

REDETECT_TABLES = False


def _nonfixture_load_tatr_tables():
    with open("data/test/references/tatr_tables.json", "r") as f:
        tatr_tables = json.load(f)
    return tatr_tables


def get_tables_for_pdf(
    docs_bulk,
    detector: AutoTableDetector,
    formatter: AutoTableFormatter,
    tatr_tables,
    n,
    REDETECT_TABLES=REDETECT_TABLES,
):
    if tatr_tables is None:
        tatr_tables = _nonfixture_load_tatr_tables()

    print("Making tables for pdf", n)
    doc = docs_bulk[n - 1]

    config = TATRTableDetectorConfig()  # purposefully use old alias
    config.detector_base_threshold = 0.9
    tables = []
    if REDETECT_TABLES:
        cropped = []
        for page in doc:
            cropped += detector.extract(page)
        for crop in cropped:
            try:
                tables.append(
                    formatter.extract(crop)
                )  # , margin='auto', padding=None))
            except Exception as e:
                raise e
    else:
        for j in range(_num_tables[n]):
            as_dict = tatr_tables[f"pdf{n}_t{j}"]
            page = doc[as_dict["page_no"]]
            tables.append(TATRFormattedTable.from_dict(as_dict, page))
    return tables


def get_ditr_tables_for_pdf(
    docs_bulk,
    ditr_tables,
):
    collector = {}
    for name, obj in ditr_tables.items():
        n = re.match(r"pdf(\d+)_", name)
        if n is None:
            continue
        n = int(n.group(1))

        if not 1 <= n <= 8:
            continue

        doc = docs_bulk[n - 1]

        page = doc[obj["page_no"]]
        collector[name] = DITRFormattedTable.from_dict(obj, page)

    return collector


def dump_text(string: str, filename: str):
    """
    Helper function to dump text to a file.
    """
    dest_folder = "data/test/outputs/actual"
    os.makedirs(dest_folder, exist_ok=True)

    with open(f"{dest_folder}/{filename}", "w", encoding="utf-8") as f:
        f.write(string)
    print(f"Dumped to {dest_folder}/{filename}")
    return string


@pytest.fixture(scope="session")
def cropped_tables():
    with open("data/test/references/cropped_tables.json", "r") as f:
        yield json.load(f)


@pytest.fixture(scope="session")
def tatr_tables():
    yield _nonfixture_load_tatr_tables()


@pytest.fixture(scope="session")
def tatr_csvs():
    with open("data/test/references/tatr_csvs.json", "r") as f:
        yield json.load(f)


@pytest.fixture(scope="session")
def ditr_tables(docs_bulk):
    with open("data/test/references/ditr_tables.json", "r") as f:
        obj = json.load(f)
        yield get_ditr_tables_for_pdf(docs_bulk, obj)


@pytest.fixture(scope="session")
def ditr_csvs():
    with open("data/test/references/ditr_csvs.json", "r") as f:
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


def pytest_sessionstart(session):
    import os

    os.makedirs("data/test/outputs/actual", exist_ok=True)
    os.makedirs("data/test/outputs/ditr", exist_ok=True)
    os.makedirs("data/test/outputs/df", exist_ok=True)
