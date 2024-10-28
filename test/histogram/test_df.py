import json
import os

import pytest
from gmft.presets import ingest_pdf
from gmft.formatters.histogram import HistogramFormatter

from ._df_data import csvs


histf = HistogramFormatter()

def try_jth_table(tables, pdf_no, j):
    global histf
    ct = tables[j] # reformat it using histogram
    ft = histf.extract(ct)
    df = ft.df()


    if f"pdf{pdf_no}_t{j}" in csvs:
        expected = csvs[f"pdf{pdf_no}_t{j}"]
    else:
        expected = f"test/outputs/bulk/pdf{pdf_no}_t{j}.csv"
        assert os.path.exists(expected), f"Extra df: pdf {pdf_no} and table {j} not found"
        with open(expected, encoding='utf-8') as f:
            expected = f.read()
    
    actual = df.to_csv(index=False, lineterminator="\n")
    if not expected == actual:
        # write to file
        debug_img = ft.visualize()
        debug_img.save(f"test/outputs/histogram/pdf{pdf_no}_t{j}.png")
        df.to_csv(f"test/outputs/histogram/pdf{pdf_no}_t{j}.csv", index=False)
        # copy over the old csv as well
        with open(f"test/outputs/histogram/pdf{pdf_no}_t{j}.old.csv", "w", encoding='utf-8') as f:
            f.write(expected)
    assert expected == actual, f"Mismatch in csv files for pdf {pdf_no} and table {j}"
    return ft

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
        pass
        # with pytest.raises(ValueError, match="The identified boxes have significant overlap"):
        #     try_jth_table(pdf1_tables, 1, 9)
        # ft = try_jth_table(pdf1_tables, 1, 9)
        # assert ft.outliers.get("high overlap")
        # assert 0.45 < ft.outliers.get("high overlap") < 0.5
    


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
        pass # empty
        # try_jth_table(pdf4_tables, 4, 0)
    def test_bulk_pdf4_t1(self, pdf4_tables):
        try_jth_table(pdf4_tables, 4, 1)

class TestPdf5:

    def test_bulk_pdf5_t0(self, pdf5_tables):
        pass # this one just doesn't work very well
        # TODO make it work based on minima
        # try_jth_table(pdf5_tables, 5, 0)
        # assert pdf5_tables[0]._projecting_indices == [15, 18, 22, 29]

    def test_bulk_pdf5_t1(self, pdf5_tables):
        try_jth_table(pdf5_tables, 5, 1)
        # TODO make it work based on splitting
    
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
    

    