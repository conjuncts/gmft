import json
import pytest
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import TableDetector
from gmft.table_function import TATRTableFormatter


@pytest.fixture
def doc_tiny():
    doc = PyPDFium2Document("test/samples/tiny.pdf")
    yield doc
    # cleanup
    doc.close()



def test_tiny_df(doc_tiny):
    detector = TableDetector()
    tables = []
    for page in doc_tiny:
        tables.extend(detector.extract(page))
    
    assert len(tables) == 1
    table = tables[0]
    formatter = TATRTableFormatter()
    ft = formatter.extract(table)
    ft.df().to_csv("test/outputs/tiny_df.csv", index=False)
    with open("test/outputs/tiny_df.info", "w") as f:
        # ft.to_dict()
        json.dump(ft.to_dict(), f, indent=4)
    