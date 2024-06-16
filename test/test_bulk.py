import json
import os
import pytest
from gmft.pdf_bindings.bindings_pdfium import PyPDFium2Document
from gmft.presets import ingest_pdf
from gmft.table_detection import TableDetector
from gmft.table_function import TATRFormattedTable, TATRTableFormatter


@pytest.fixture
def docs():
    docs = []
    for i in range(1, 9):
        doc = PyPDFium2Document(f"test/samples/{i}.pdf")
        docs.append(doc)

    yield docs
    # cleanup
    for doc in docs:
        doc.close()

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
def test_bulk_pdf1(docs):
    i = 0
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"
                
def test_bulk_pdf2(docs):
    i = 1
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf3(docs):
    i = 2
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf4(docs):
    i = 3
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf5(docs):
    i = 4
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf6(docs):
    i = 5
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf7(docs):
    i = 6
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

def test_bulk_pdf8(docs):
    i = 7
    doc = docs[i]
    # for i, doc in enumerate(docs):
    for j in range(num_tables[i+1]):
        with open(f"test/outputs/bulk/pdf{i+1}_t{j}.info", "r") as f:
            
            as_dict = json.load(f)
            page_no = as_dict["page_no"]
            page = doc[page_no]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            try:
                df = ft.df()
                expected = f"test/outputs/bulk/pdf{i+1}_t{j}.csv"
                assert os.path.exists(expected), f"Extra df: pdf {i+1} and table {j} not found"
                with open(expected, encoding='utf-8') as f:
                    assert df.to_csv(index=False, lineterminator="\n") == f.read(), f"Mismatch in csv files for pdf {i+1} and table {j}"
            except ValueError as e:
                assert not os.path.exists(f"test/outputs/bulk/pdf{i+1}_t{j}.csv"), f"Failed to create df in pdf {i+1} and table {j}"

        
    

if __name__ == "__main__":
    # generate the files
    formatter = TATRTableFormatter()
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