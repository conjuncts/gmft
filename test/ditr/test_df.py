
from gmft.formatters.ditr import DITRFormattedTable


def get_ft(ditr_tables, namespace, pdf):
    obj = ditr_tables[namespace]
    page = pdf[obj['page_no']]
    return DITRFormattedTable.from_dict(obj, page)

def try_table(want, ditr_tables, ditr_csvs, pdf):
    ft = get_ft(ditr_tables, want, pdf)
    expected = ditr_csvs[want]
    actual = ft.df().to_csv(index=False, lineterminator='\n')
    if expected != actual:
        # save images and csvs
        debug_img = ft.visualize()
        debug_img.save(f"test/outputs/ditr/{want}.png")
        ft.df().to_csv(f"test/outputs/ditr/{want}.csv", index=False)
        with open(f"test/outputs/ditr/{want}.old.csv", "w", encoding='utf-8') as f:
            f.write(expected)
    assert expected == actual, f"Mismatch in csv files for {want}"

class TestPdf1:


    def test_bulk_pdf1_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t0', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t1', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t2(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t2', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t3(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t3', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t4(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t4', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t5(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t5', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t6(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t6', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t7(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t7', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t8(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf1_t8', ditr_tables, ditr_csvs, docs_bulk[1-1])
    def test_bulk_pdf1_t9(self, ditr_tables, ditr_csvs, docs_bulk):
        pass



class TestPdf2:

    def test_bulk_pdf2_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf2_t0', ditr_tables, ditr_csvs, docs_bulk[2-1])
    def test_bulk_pdf2_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf2_t1', ditr_tables, ditr_csvs, docs_bulk[2-1])
    def test_bulk_pdf2_t2(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf2_t2', ditr_tables, ditr_csvs, docs_bulk[2-1])
    def test_bulk_pdf2_t3(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf2_t3', ditr_tables, ditr_csvs, docs_bulk[2-1])

class TestPdf3:

    def test_bulk_pdf3_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf3_t0', ditr_tables, ditr_csvs, docs_bulk[3-1])
    def test_bulk_pdf3_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf3_t1', ditr_tables, ditr_csvs, docs_bulk[3-1])
    def test_bulk_pdf3_t2(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf3_t2', ditr_tables, ditr_csvs, docs_bulk[3-1])
    def test_bulk_pdf3_t3(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf3_t3', ditr_tables, ditr_csvs, docs_bulk[3-1])

class TestPdf4:

    def test_bulk_pdf4_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        pass # empty
        # try_jth_table(pdf4_tables, tatr_csvs, 4, 0)
    def test_bulk_pdf4_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf4_t1', ditr_tables, ditr_csvs, docs_bulk[4-1])

class TestPdf5:

    def test_bulk_pdf5_t0(self, pdf5_tables):
        pass # this one just doesn't work very well
        # TODO make it work based on minima
        # try_jth_table(pdf5_tables, 5, 0)
        # assert pdf5_tables[0]._projecting_indices == [15, 18, 22, 29]

    def test_bulk_pdf5_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf5_t1', ditr_tables, ditr_csvs, docs_bulk[5-1])
        # TODO make it work based on splitting
    
class TestPdf6:

    def test_bulk_pdf6_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf6_t0', ditr_tables, ditr_csvs, docs_bulk[6-1])
    def test_bulk_pdf6_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf6_t1', ditr_tables, ditr_csvs, docs_bulk[6-1])
    def test_bulk_pdf6_t2(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf6_t2', ditr_tables, ditr_csvs, docs_bulk[6-1])

class TestPdf7:

    def test_bulk_pdf7_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf7_t0', ditr_tables, ditr_csvs, docs_bulk[7-1])
    def test_bulk_pdf7_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf7_t1', ditr_tables, ditr_csvs, docs_bulk[7-1])
    def test_bulk_pdf7_t2(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf7_t2', ditr_tables, ditr_csvs, docs_bulk[7-1])

class TestPdf8:

    def test_bulk_pdf8_t0(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf8_t0', ditr_tables, ditr_csvs, docs_bulk[8-1])
    def test_bulk_pdf8_t1(self, ditr_tables, ditr_csvs, docs_bulk):
        try_table('pdf8_t1', ditr_tables, ditr_csvs, docs_bulk[8-1])
    

    