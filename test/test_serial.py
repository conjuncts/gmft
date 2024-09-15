
# test to_dict and from_dict



import json
import pytest
from gmft.pdf_bindings import BasePage
from gmft import CroppedTable
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.table_detection import RotatedCroppedTable
from gmft.table_function import TATRFormattedTable


@pytest.fixture(scope="session")
def doc_9():
    doc = PyPDFium2Document("test/samples/9.pdf")
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

def test_FormattedTable_from_dict_backcompat(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    with open("test/outputs/tiny_df.old.info") as f:
        table_dict = json.load(f)
    formatted_table = TATRFormattedTable.from_dict(table_dict, page)
    df = formatted_table.df()
    # get csv as string
    csv_str = df.to_csv(index=False, lineterminator='\n')
    
    assert csv_str == """Name,Celsius,Fahrenheit
Water Freezing Point,0,32
Water Boiling Point,100,212
Body Temperature,37,98.6
"""

def test_FormattedTable_from_dict(doc_tiny):
    # create a CroppedTable object
    page = doc_tiny[0]
    with open("test/outputs/tiny_df.old.info") as f:
        table_dict = json.load(f)
    formatted_table = TATRFormattedTable.from_dict(table_dict, page)
    df = formatted_table.df()
    # get csv as string
    csv_str = df.to_csv(index=False, lineterminator='\n')
    
    assert csv_str == """Name,Celsius,Fahrenheit
Water Freezing Point,0,32
Water Boiling Point,100,212
Body Temperature,37,98.6
"""

def test_FormattedTable_to_dict(doc_tiny):
    # assert that to_dict o from_dict is identity
    page = doc_tiny[0]
    with open("test/outputs/tiny_df.info") as f:
        table_dict = json.load(f)
    dict2table = TATRFormattedTable.from_dict(table_dict, page)
    dict2table2dict = dict2table.to_dict()
    
    with open("test/outputs/actual/tiny_df.info", "w") as f:
        json.dump(dict2table2dict, f, indent=4)
    assert dict2table2dict == table_dict

def test_FormattedTable_to_dict_backcompat(doc_tiny):
    # assert that to_dict o from_dict is identity
    page = doc_tiny[0]
    with open("test/outputs/tiny_df.old.info") as f:
        table_dict = json.load(f)
    dict2table = TATRFormattedTable.from_dict(table_dict, page)
    dict2table2dict = dict2table.to_dict()
    
    with open("test/outputs/tiny_df.info", "r") as f:
        want = json.load(f)
    
    assert dict2table2dict == want


def test_RotatedCroppedTable_from_to_dict(doc_9):
    # create a CroppedTable object
    page = doc_9[8]
    with open("test/outputs/bulk/pdf9_t4.info") as f:
        table_dict = json.load(f)
    dict2table = TATRFormattedTable.from_dict(table_dict, page)
    assert isinstance(dict2table, RotatedCroppedTable)
    assert dict2table.angle == 90
    
    dict2table2dict = dict2table.to_dict()
    assert dict2table2dict == table_dict
    
    # test a simpler subset
    dict2simple = RotatedCroppedTable.from_dict(table_dict, page)
    assert dict2simple.to_dict() == {
        "filename": "test/samples/9.pdf",
        "page_no": 8,
        "bbox": [
            71.3222885131836,
            54.75971984863281,
            529.1936645507812,
            716.1232299804688
        ],
        "confidence_score": 0.9999405145645142,
        "label": 1,
        "angle": 90
    }
    
    
    