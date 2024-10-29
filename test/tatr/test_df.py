import json
import os
import pytest
from gmft.auto import AutoFormatConfig, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.presets import ingest_pdf
from gmft.detectors.tatr import TATRDetectorConfig
from gmft.formatters.tatr import TATRFormattedTable
# from .conftest import REDETECT_TABLES


# non-determinism of transformers means this might not always pass
# (ie. dependence on environment - colab/local) 



# @pytest.fixture(scope="module")
# def formatter():
#     # try out microsoft/table-transformer-structure-recognition-v1.1-all
#     config = AutoFormatConfig()
#     config.detector_path = "microsoft/table-transformer-structure-recognition-v1.1-all"
#     config.no_timm = False
#     yield AutoTableFormatter(config)





def try_jth_table(tables, tatr_csvs, pdf_no, j, config=None, REDETECT_TABLES=False):
    
    if config is None:
        config = AutoFormatConfig()
        config.large_table_threshold = 20
        config.verbosity = 3
        config.semantic_spanning_cells = False
        # config.semantic_spanning_cells = True
        
    # note that config_overrides and config are both not a dict

    ft = tables[j]
    # try:
    df = ft.df(config_overrides=config)
    assert f'pdf{pdf_no}_t{j}' in tatr_csvs, f"Extra df: pdf {pdf_no} and table {j} not found in known csvs"
    expected = tatr_csvs[f'pdf{pdf_no}_t{j}']
    actual = df.to_csv(index=False, lineterminator="\n")
    if not expected == actual:
        # write images
        debug_img = ft.visualize(effective=True, show_labels=False, return_img=True)
        debug_img.save(f"test/outputs/actual/pdf{pdf_no}_t{j}.png")

        # write csvs
        df.to_csv(f"test/outputs/actual/pdf{pdf_no}_t{j}.csv", index=False)
        with open(f"test/outputs/actual/pdf{pdf_no}_t{j}.old.csv", "w", encoding='utf-8') as f:
            f.write(expected)
        if REDETECT_TABLES:
            with open(f"test/outputs/actual/pdf{pdf_no}_t{j}.info", "w") as f:
                json.dump(ft.to_dict(), f, indent=2)
    assert expected == actual, f"Mismatch in csv files for pdf {pdf_no} and table {j}"
    return ft

class TestPdf1:


    def test_bulk_pdf1_t0(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 0)
    def test_bulk_pdf1_t1(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 1)
    def test_bulk_pdf1_t2(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 2)
    def test_bulk_pdf1_t3(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 3)
    def test_bulk_pdf1_t4(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 4)
    def test_bulk_pdf1_t5(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 5)
    def test_bulk_pdf1_t6(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 6)
    def test_bulk_pdf1_t7(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 7)
    def test_bulk_pdf1_t8(self, pdf1_tables, tatr_csvs):
        try_jth_table(pdf1_tables, tatr_csvs, 1, 8)
    def test_bulk_pdf1_t9(self, pdf1_tables, tatr_csvs):
        # with pytest.raises(ValueError, match="The identified boxes have significant overlap"):
        #     try_jth_table(pdf1_tables, tatr_csvs, 1, 9)
        ft = try_jth_table(pdf1_tables, tatr_csvs, 1, 9)
        assert ft.outliers.get("high overlap")
        assert 0.45 < ft.outliers.get("high overlap") < 0.5
    


class TestPdf2:
    
    

    def test_bulk_pdf2_t0(self, pdf2_tables, tatr_csvs):
        try_jth_table(pdf2_tables, tatr_csvs, 2, 0)
    def test_bulk_pdf2_t1(self, pdf2_tables, tatr_csvs):
        try_jth_table(pdf2_tables, tatr_csvs, 2, 1)
        # hint: subtract 2 from the line no to get the proj. index (assume 1 header)
        assert pdf2_tables[1]._projecting_indices == [9, 12, 16]
    def test_bulk_pdf2_t2(self, pdf2_tables, tatr_csvs):
        try_jth_table(pdf2_tables, tatr_csvs, 2, 2)
        assert pdf2_tables[2]._projecting_indices == [0, 5]
    def test_bulk_pdf2_t3(self, pdf2_tables, tatr_csvs):
        try_jth_table(pdf2_tables, tatr_csvs, 2, 3)
        assert pdf2_tables[3]._projecting_indices == [12]

class TestPdf3:

    def test_bulk_pdf3_t0(self, pdf3_tables, tatr_csvs):
        try_jth_table(pdf3_tables, tatr_csvs, 3, 0)
    def test_bulk_pdf3_t1(self, pdf3_tables, tatr_csvs):
        try_jth_table(pdf3_tables, tatr_csvs, 3, 1)
    def test_bulk_pdf3_t2(self, pdf3_tables, tatr_csvs):
        try_jth_table(pdf3_tables, tatr_csvs, 3, 2)
        assert pdf3_tables[2]._projecting_indices == [0, 8]
    def test_bulk_pdf3_t3(self, pdf3_tables, tatr_csvs):
        try_jth_table(pdf3_tables, tatr_csvs, 3, 3)

class TestPdf4:

    def test_bulk_pdf4_t0(self, pdf4_tables, tatr_csvs):
        try_jth_table(pdf4_tables, tatr_csvs, 4, 0)
    def test_bulk_pdf4_t1(self, pdf4_tables, tatr_csvs):
        try_jth_table(pdf4_tables, tatr_csvs, 4, 1)
        assert pdf4_tables[1]._projecting_indices == [0, 14]

class TestPdf5:

    def test_bulk_pdf5_t0(self, pdf5_tables, tatr_csvs):
        try_jth_table(pdf5_tables, tatr_csvs, 5, 0)
        assert pdf5_tables[0]._projecting_indices == [15, 18, 22, 29]
    def test_bulk_pdf5_t1(self, pdf5_tables, tatr_csvs):
        try_jth_table(pdf5_tables, tatr_csvs, 5, 1)
        assert pdf5_tables[1]._projecting_indices == [13, 16, 22, 26]
    
class TestPdf6:

    def test_bulk_pdf6_t0(self, pdf6_tables, tatr_csvs):
        try_jth_table(pdf6_tables, tatr_csvs, 6, 0)
    def test_bulk_pdf6_t1(self, pdf6_tables, tatr_csvs):
        try_jth_table(pdf6_tables, tatr_csvs, 6, 1)
    def test_bulk_pdf6_t2(self, pdf6_tables, tatr_csvs):
        try_jth_table(pdf6_tables, tatr_csvs, 6, 2)

class TestPdf7:

    def test_bulk_pdf7_t0(self, pdf7_tables, tatr_csvs):
        try_jth_table(pdf7_tables, tatr_csvs, 7, 0)
    def test_bulk_pdf7_t1(self, pdf7_tables, tatr_csvs):
        try_jth_table(pdf7_tables, tatr_csvs, 7, 1)
    def test_bulk_pdf7_t2(self, pdf7_tables, tatr_csvs):
        try_jth_table(pdf7_tables, tatr_csvs, 7, 2)

class TestPdf8:

    def test_bulk_pdf8_t0(self, pdf8_tables, tatr_csvs):
        try_jth_table(pdf8_tables, tatr_csvs, 8, 0)
    def test_bulk_pdf8_t1(self, pdf8_tables, tatr_csvs):
        try_jth_table(pdf8_tables, tatr_csvs, 8, 1)
    

    