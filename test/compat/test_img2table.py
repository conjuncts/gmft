import pytest
from gmft.detectors.img2table import Img2TableDetector, Img2TablePDFDocument
from gmft.formatters.with_img2table import Img2TableFormatter
from gmft.table_detection import CroppedTable

_ = pytest.importorskip("img2table")

# this is really also testing _infer_line_breaks

def test_i2t_pdf_compat(doc_tiny):
    """check that we are able to wrap arbitrary pdf types, including pypdfium2 (native is pymupdf)"""
    i2tdoc = Img2TablePDFDocument(doc_tiny)
    
    extracted_tables = i2tdoc.extract_tables(ocr=None,
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=False,
        min_confidence=50)
    
    page0tables = extracted_tables[0]
    assert len(page0tables) == 1
    assert page0tables[0].df.to_csv(index=False, sep='\t', lineterminator='\n') == """0	1	2
Name	Celsius	Fahrenheit
Water Freezing Point	0	32
Water Boiling Point	100	212
Body Temperature	37	98.6
"""


def test_i2t_pdf_compat(doc_tiny):
    """likewise check that the croppedtable and detector pipeline works for these new documents"""
    i2tdoc = Img2TablePDFDocument(doc_tiny)
    
    extracted_tables = i2tdoc.extract_tables(ocr=None,
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=False,
        min_confidence=50)
    
    page0tables = extracted_tables[0]
    assert len(page0tables) == 1
    assert page0tables[0].df.to_csv(index=False, sep='\t', lineterminator='\n') == """0	1	2
Name	Celsius	Fahrenheit
Water Freezing Point	0	32
Water Boiling Point	100	212
Body Temperature	37	98.6
"""

def test_i2t_detect(doc_tiny):
    detector = Img2TableDetector()
    cts = detector.extract(doc_tiny[0])
    assert len(cts) == 1
    assert cts[0].df().to_csv(index=False, sep='\t', lineterminator='\n') == """0	1	2
Name	Celsius	Fahrenheit
Water Freezing Point	0	32
Water Boiling Point	100	212
Body Temperature	37	98.6
"""
    
    
    
# def test_i2t_format(doc_tiny):
#     ct = CroppedTable.from_dict({
#         'filename': 'test/samples/tiny.pdf',
#         'page_number': 0,
#         'bbox': [
#             76.66205596923828,
#             162.82687377929688,
#             440.9659729003906,
#             248.67056274414062
#         ],
#         'confidence_score': 1,
#         'label': 0}, doc_tiny[0])
    
#     fmtr = Img2TableFormatter()
    
#     formatted = fmtr.extract(ct)
#     assert formatted.df().to_csv(index=False, sep='\t', lineterminator='\n') == """0	1	2
# Name	Celsius	Fahrenheit
# Water Freezing Point	0	32
# Water Boiling Point	100	212
# Body Temperature	37	98.6
# """
