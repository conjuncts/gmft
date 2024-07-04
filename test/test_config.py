
# test to_dict and from_dict



import json
import pytest
from gmft.pdf_bindings import BasePage
from gmft import CroppedTable
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.table_detection import RotatedCroppedTable
from gmft.table_function import AutoFormatConfig, TATRFormattedTable

def test_config(docs_bulk):
    # Test that configuration overrides work
    config = AutoFormatConfig()
    config.remove_null_rows = False
    with open(f"test/outputs/bulk/pdf7_t2.info", "r") as f:
            
        as_dict = json.load(f)
        page_no = as_dict["page_no"]
        page = docs_bulk[6][page_no]
        ft = TATRFormattedTable.from_dict(as_dict, page)
        
        df = ft.df(config_overrides=config)
    expected = """Genotype,Q,Amino R,acid 70 P,H,Amino C,acid M,91 L,Total
,,,,,,,,
,,,,,,,,
1a,2%,98%,-,-,100%,-,-,920
1b,60%,35%,-,4%,1%,71%,28%,2022
2,-,100%,-,-,39%,4%,58%,83
3,-,93%,6%,-,99%,-,-,204
4,5%,95%,-,-,100%,-,-,19
5,86%,14%,-,-,-,-,100%,14
6,60%,13%,13%,15%,100%,-,-,55
"""
    assert df.to_csv(index=False, lineterminator='\n') == expected