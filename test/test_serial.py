
# test to_dict and from_dict



import json
import pytest
from gmft.pdf_bindings import BasePage
from gmft import CroppedTable
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_function import TATRFormattedTable

@pytest.fixture
def doc_tiny():
    doc = PyPDFium2Document("test/samples/tiny.pdf")
    yield doc
    # cleanup
    doc.close()

def test_CroppedTable_to_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    table = CroppedTable(page, (10, 10, 300, 300), 0.9, 0)
    table_dict = table.to_dict()
    assert table_dict == {
        'filename': "test/samples/tiny.pdf",
        'page_no': 0,
        'bbox': (10, 10, 300, 300),
        'confidence_score': 0.9,
        'label': 0
    }

def test_CroppedTable_from_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    table = CroppedTable.from_dict({
        'filename': "test/samples/tiny.pdf",
        'page_no': 0,
        'bbox': (10, 10, 300, 150),
        'confidence_score': 0.9,
        'label': 0
    }, page)
    
    print(table.text())
    assert table.text() == """Simple document
Lorem ipsum dolor sit amet, consectetur adipiscing
Table 1. Selected Numbers"""

def test_FormattedTable_from_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    with open("test/outputs/tiny_df.info") as f:
        table_dict = json.load(f)
    formatted_table = TATRFormattedTable.from_dict(table_dict, page)
    df = formatted_table.df()
    # get csv as string
    csv_str = df.to_csv(index=False)
    
    assert csv_str == """Name,Celsius,Fahrenheit\r
Water Freezing Point,0,32\r
Water Boiling Point,100,212\r
Body Temperature,37,98.6\r
"""

def test_FormattedTable_to_dict(doc_tiny):
    # assert that to_dict o from_dict is identity
    page = doc_tiny[0]
    with open("test/outputs/tiny_df.info") as f:
        table_dict = json.load(f)
    formatted_table = TATRFormattedTable.from_dict(table_dict, page)
    formatted_table_dict = formatted_table.to_dict()
    assert formatted_table_dict == table_dict

