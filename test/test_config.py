
# # test to_dict and from_dict



# import json
# import pytest
# from gmft.pdf_bindings import BasePage
# from gmft.auto import AutoFormatConfig, CroppedTable
# from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
# from gmft.table_detection import RotatedCroppedTable
# from gmft.table_function import TATRFormattedTable

# def test_config(docs_bulk):
#     # Test that configuration overrides work
#     config = AutoFormatConfig()
#     config.remove_null_rows = False
#     with open(f"test/outputs/bulk/pdf7_t2.info", "r") as f:
            
#         as_dict = json.load(f)
#         page_no = as_dict["page_no"]
#         page = docs_bulk[6][page_no]
#         ft = TATRFormattedTable.from_dict(as_dict, page)
        
#         df = ft.df(config_overrides=config)
#     expected = """Genotype,Q,Amino\\nR,acid 70\\nP,H,Amino\\nC,acid\\nM,91\\nL,Total
# ,,,,,,,,
# ,,,,,,,,
# 1a,2%,98%,-,-,100%,-,-,920
# 1b,60%,35%,-,4%,1%,71%,28%,2022
# 2,-,100%,-,-,39%,4%,58%,83
# 3,-,93%,6%,-,99%,-,-,204
# 4,5%,95%,-,-,100%,-,-,19
# 5,86%,14%,-,-,-,-,100%,14
# 6,60%,13%,13%,15%,100%,-,-,55
# """
#     assert df.to_csv(index=False, lineterminator='\n') == expected

from gmft._dataclasses import with_config
from gmft.formatters.tatr import TATRFormatConfig


def test_overrides():
    config = TATRFormatConfig(verbosity=99, enable_multi_header=True)
    
    overrides = TATRFormatConfig(force_large_table_assumption=True, enable_multi_header=False)
    
    result = with_config(config, overrides)
    assert result.verbosity == 1 # CAUTION! since overrides completely replaces config, 
    # it gets reset to the setting default, which is 1
    assert result.force_large_table_assumption == True
    assert result.enable_multi_header == False
    
    # now, try using the dict method
    result = with_config(config, {
        "force_large_table_assumption": True,
        "enable_multi_header": False
    })
    assert result.verbosity == 99 # dict preserves set/unset, which was the old behavior
    assert result.force_large_table_assumption == True
    assert result.enable_multi_header == False
    