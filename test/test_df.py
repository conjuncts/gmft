import json
import os
import pytest
from gmft import AutoFormatConfig, AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.presets import ingest_pdf
from gmft.table_detection import TableDetectorConfig
from gmft.table_function import TATRFormattedTable
from .conftest import REDETECT_TABLES


# non-determinism of transformers means this might not always pass
# (ie. dependence on environment - colab/local) 



# @pytest.fixture(scope="module")
# def formatter():
#     # try out microsoft/table-transformer-structure-recognition-v1.1-all
#     config = AutoFormatConfig()
#     config.detector_path = "microsoft/table-transformer-structure-recognition-v1.1-all"
#     config.no_timm = False
#     yield AutoTableFormatter(config)





def try_jth_table(tables, pdf_no, j, config=None, REDETECT_TABLES=False):
    
    if config is None:
        config = AutoFormatConfig()
        config.large_table_threshold = 20
        config.verbosity = 3
        # config.semantic_spanning_cells = True
        
    # note that config_overrides and config are both not a dict

    ft = tables[j]
    # try:
    df = ft.df(config_overrides=config)
    expected = f"test/outputs/bulk/pdf{pdf_no}_t{j}.csv"
    assert os.path.exists(expected), f"Extra df: pdf {pdf_no} and table {j} not found"
    with open(expected, encoding='utf-8') as f:
        expected = f.read()
        actual = df.to_csv(index=False, lineterminator="\n")
        if not expected == actual:
            # write to file
            # debug_img = ft.image() # visualize(effective=True, show_labels=False)
            debug_img = ft.visualize(effective=True, show_labels=False, return_img=True)
            debug_img.save(f"test/outputs/actual/pdf{pdf_no}_t{j}.png")
            df.to_csv(f"test/outputs/actual/pdf{pdf_no}_t{j}.csv", index=False)
            # copy over the old csv as well
            with open(f"test/outputs/actual/pdf{pdf_no}_t{j}.old.csv", "w", encoding='utf-8') as f:
                f.write(expected)
            if REDETECT_TABLES:
                with open(f"test/outputs/actual/pdf{pdf_no}_t{j}.info", "w") as f:
                    json.dump(ft.to_dict(), f, indent=2)
        assert expected == actual, f"Mismatch in csv files for pdf {pdf_no} and table {j}"
    # except ValueError as e:
        # assert not os.path.exists(f"test/outputs/bulk/pdf{pdf_no}_t{j}.csv"), f"Failed to create df in pdf {pdf_no} and table {j}"

class TestPdf1:


    def test_bulk_pdf1_t0(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 0)
    def test_bulk_pdf1_t1(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 1)
    def test_bulk_pdf1_t2(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 2)
    def test_bulk_pdf1_t3(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 3)
    def test_bulk_pdf1_t4(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 4)
    def test_bulk_pdf1_t5(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 5)
    def test_bulk_pdf1_t6(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 6)
    def test_bulk_pdf1_t7(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 7)
    def test_bulk_pdf1_t8(self, pdf1_tables):
        try_jth_table(pdf1_tables, 1, 8)
    def test_bulk_pdf1_t9(self, pdf1_tables):
        with pytest.raises(ValueError, match="The identified boxes have significant overlap"):
            try_jth_table(pdf1_tables, 1, 9)
    


class TestPdf2:
    
    

    def test_bulk_pdf2_t0(self, pdf2_tables):
        try_jth_table(pdf2_tables, 2, 0)
    def test_bulk_pdf2_t1(self, pdf2_tables):
        try_jth_table(pdf2_tables, 2, 1)
    def test_bulk_pdf2_t2(self, pdf2_tables):
        try_jth_table(pdf2_tables, 2, 2)
    def test_bulk_pdf2_t3(self, pdf2_tables):
        try_jth_table(pdf2_tables, 2, 3)

class TestPdf3:

    def test_bulk_pdf3_t0(self, pdf3_tables):
        try_jth_table(pdf3_tables, 3, 0)
    def test_bulk_pdf3_t1(self, pdf3_tables):
        try_jth_table(pdf3_tables, 3, 1)
    def test_bulk_pdf3_t2(self, pdf3_tables):
        try_jth_table(pdf3_tables, 3, 2)
    def test_bulk_pdf3_t3(self, pdf3_tables):
        try_jth_table(pdf3_tables, 3, 3)

class TestPdf4:

    def test_bulk_pdf4_t0(self, pdf4_tables):
        try_jth_table(pdf4_tables, 4, 0)
    def test_bulk_pdf4_t1(self, pdf4_tables):
        try_jth_table(pdf4_tables, 4, 1)

class TestPdf5:

    def test_bulk_pdf5_t0(self, pdf5_tables):
        try_jth_table(pdf5_tables, 5, 0)
    def test_bulk_pdf5_t1(self, pdf5_tables):
        try_jth_table(pdf5_tables, 5, 1)
    
class TestPdf6:

    def test_bulk_pdf6_t0(self, pdf6_tables):
        try_jth_table(pdf6_tables, 6, 0)
    def test_bulk_pdf6_t1(self, pdf6_tables):
        try_jth_table(pdf6_tables, 6, 1)
    def test_bulk_pdf6_t2(self, pdf6_tables):
        try_jth_table(pdf6_tables, 6, 2)

class TestPdf7:

    def test_bulk_pdf7_t0(self, pdf7_tables):
        try_jth_table(pdf7_tables, 7, 0)
    def test_bulk_pdf7_t1(self, pdf7_tables):
        try_jth_table(pdf7_tables, 7, 1)
    def test_bulk_pdf7_t2(self, pdf7_tables):
        try_jth_table(pdf7_tables, 7, 2)

class TestPdf8:

    def test_bulk_pdf8_t0(self, pdf8_tables):
        try_jth_table(pdf8_tables, 8, 0)
    def test_bulk_pdf8_t1(self, pdf8_tables):
        try_jth_table(pdf8_tables, 8, 1)
    

    

if __name__ == "__main__":
    # generate the files
    formatter = AutoTableFormatter()
    for i in range(9, 10):
        tables, doc = ingest_pdf(f"test/samples/{i}.pdf")
        try:
            fts = [formatter.extract(table) for table in tables]
        except Exception as e:
            print(f"Error in pdf {i}")
            
        for j, ft in enumerate(fts):
            with open(f"test/outputs/bulk/pdf{i}_t{j}.info", "w") as f:
                json.dump(ft.to_dict(), f, indent=4)
            try: 
                ft.df().to_csv(f"test/outputs/bulk/pdf{i}_t{j}.csv", index=False)
            except Exception as e:
                print(f"df Error in pdf {i} and table {j}")
        doc.close()
        break