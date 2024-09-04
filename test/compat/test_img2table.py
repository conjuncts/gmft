import pytest
from gmft.detectors.detect_img2table import Img2TablePDFDocument

_ = pytest.importorskip("img2table")

# this is really also testing _infer_line_breaks

def test_i2t_detect(doc_tiny):
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
    
    