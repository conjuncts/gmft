import json
import os
import pytest
from gmft import AutoFormatConfig, AutoTableFormatter
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.presets import ingest_pdf
from gmft.table_function import TATRFormattedTable



REDETECT_TABLES = True

num_tables = {
    1: 10,
    2: 4,
    3: 4,
    4: 2, 
    5: 2, 
    6: 3, 
    7: 3, 
    8: 2,
}

def trial_pdf(docs_bulk, detector, formatter: AutoTableFormatter, i):
    doc = docs_bulk[i]
    # for i, doc in enumerate(docs_bulk):
    
    config = AutoFormatConfig()
    config.formatter_base_threshold = 0.9
    config.large_table_threshold = 20
    # config.large_table_threshold = 0
    # config.large_table_row_overlap_threshold = -1
    # config.remove_null_rows = False
    
    tables = []
    if REDETECT_TABLES:
        cropped = []
        for page in doc:
            cropped += detector.extract(page)
        for crop in cropped:
            try:
                tables.append(formatter.extract(crop))
            except Exception as e:
                # print(e)
                raise e
                # pass
                # tables.append(None)
    else:
        for j in range(num_tables[i+1]):
            with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
                as_dict = json.load(f)
                page_no = as_dict["page_no"]
                page = doc[page_no]
                tables.append(TATRFormattedTable.from_dict(as_dict, page))
        
    for j, ft in enumerate(tables):
        try:
            df = ft.df(config_overrides=config)
            expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
            assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
            with open(expected, encoding='utf-8') as f:
                expected = f.read()
                actual = df.to_csv(index=False, lineterminator="\n")
                if not expected == actual:
                    # write to file
                    # debug_img = ft.image() # visualize(effective=True, show_labels=False)
                    debug_img = ft.visualize(effective=True, show_labels=False, return_img=True)
                    debug_img.save(f"test/outputs/actual/pdf{i+1}_t{j}.png")
                    with open(f"test/outputs/actual/pdf{i+1}_t{j}.csv", "w", encoding='utf-8') as f:
                        f.write(actual)
                    if REDETECT_TABLES:
                        with open(f"test/outputs/actual/pdf{i+1}_t{j}.info", "w") as f:
                            json.dump(ft.to_dict(), f, indent=2)
                assert expected == actual, f"Mismatch in csv files for pdf {i+1} and table {j}"
        except ValueError as e:
            assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf1(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=0)
            
def test_bulk_pdf2(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=1)

def test_bulk_pdf3(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=2)

def test_bulk_pdf4(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=3)

def test_bulk_pdf5(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=4)

def test_bulk_pdf6(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=5)

def test_bulk_pdf7(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=6)
    
def test_bulk_pdf8(docs_bulk, detector, formatter):
    trial_pdf(docs_bulk=docs_bulk, detector=detector, formatter=formatter, i=7)


    

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