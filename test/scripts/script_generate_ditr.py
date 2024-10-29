import glob
import json
import os


def script_collect_jsons():
    """
    Converts between the legacy file-based storage system into the centralized jsons
    """
    from gmft.detectors.common import CroppedTable
    from gmft.formatters.ditr import DITRFormatter
    from gmft.formatters.tatr import TATRFormattedTable, TATRFormatter
    from gmft.pdf_bindings.pdfium import PyPDFium2Document

    from gmft.detectors.tatr import TATRDetector

    # run DITR formatting
    # search all 'test/outputs/bulk/*.info'

    formatter = DITRFormatter()
    tatr_formatter = TATRFormatter()

    
    pdfs = {}
    for filename in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'tatr', 'tiny']:
        pdfs[filename] = PyPDFium2Document(f"test/samples/{filename}.pdf")
    pdfs['attn'] = PyPDFium2Document(f"test/samples/attention.pdf")

    tatr_results = {}
    ct_results = {}
    ditr_results = {}
    ditr_csvs = {}
    
    for i in range(1, 10):
        for filename in glob.glob(f"test/outputs/bulk/pdf{i}_t*.info"):
            basename = os.path.basename(filename).replace('.info', '')

            with open(filename, encoding='utf-8') as f:
                as_dict = json.load(f)
            page = pdfs[str(i)][as_dict["page_no"]]
            ft = TATRFormattedTable.from_dict(as_dict, page)
            tatr_results[basename] = ft.to_dict()

            ct = CroppedTable.from_dict(as_dict, page)
            ct_results[basename] = ct.to_dict()

            dift = formatter.extract(ct)
            ditr_results[basename] = dift.to_dict()

            ditr_csvs[basename] = ft.df().to_csv(index=False, lineterminator='\n')
    
    
    for filename in glob.glob(f"test/outputs/pubt/pubt_p*.info"):
        basename = os.path.basename(filename).replace('.info', '')
        with open(filename, encoding='utf-8') as f:
            as_dict = json.load(f)
        page = pdfs['tatr'][as_dict["page_no"]]

        ct = CroppedTable.from_dict(as_dict, page)
        ct_results[basename] = ct.to_dict()

        ft = tatr_formatter.extract(ct)
        tatr_results[basename] = ft.to_dict()

        dift = formatter.extract(ct)
        ditr_results[basename] = dift.to_dict()

        ditr_csvs[basename] = ft.df().to_csv(index=False, lineterminator='\n')
    
    for filename in glob.glob(f"test/refs/attn/attn*.json"):
        basename = os.path.basename(filename).replace('.json', '')
        with open(filename, encoding='utf-8') as f:
            as_dict = json.load(f)
        page = pdfs['attn'][as_dict["page_no"]]
        ft = TATRFormattedTable.from_dict(as_dict, page)
        tatr_results[basename] = ft.to_dict()

        ct = CroppedTable.from_dict(as_dict, page)
        ct_results[basename] = ct.to_dict()

        dift = formatter.extract(ct)
        ditr_results[basename] = dift.to_dict()

        ditr_csvs[basename] = ft.df().to_csv(index=False, lineterminator='\n')

    # write to files
    with open("test/refs/tatr_tables.json", "w") as f:
        json.dump(tatr_results, f, indent=2)
    with open("test/refs/cropped_tables.json", "w") as f:
        json.dump(ct_results, f, indent=2)
    with open("test/refs/ditr_tables.json", "w") as f:
        json.dump(ditr_results, f, indent=2)
    with open("test/refs/ditr_csvs.json", "w") as f:
        json.dump(ditr_csvs, f, indent=2)
    

    # generate the markdown file
    import json
    import pandas as pd
    import io

    builder = ''
    for k, csv in ditr_csvs.items():
        df = pd.read_csv(io.StringIO(csv)).fillna('')

        builder += f"## {k}\n"
        builder += df.to_markdown() + '\n\n'

    with open('test/refs/ditr_tables.md', 'w', encoding='utf-8') as f:
        f.write(builder)

def script_collect_csvs():

    # collect csvs for tatr
    tatr_csvs = {}
    for i in range(1, 10):
        for filename in glob.glob(f"test/outputs/bulk/pdf{i}_t*.csv"):
            basename = os.path.basename(filename).replace('.csv', '')
            with open(filename, encoding='utf-8') as f:
                tatr_csvs[basename] = f.read()
    
    with open('test/refs/tatr_csvs.json', 'w') as f:
        json.dump(tatr_csvs, f, indent=2)

def script_generate_tatr():
    from gmft.formatters.tatr import TATRFormatter
    from gmft.presets import ingest_pdf
    formatter = TATRFormatter()
    for i in [1]:
        tables, doc = ingest_pdf(f"test/samples/{i}.pdf")
        try:
            fts = [formatter.extract(table) for table in tables]
        except Exception:
            print(f"Error in pdf {i}")
            
        for j, ft in enumerate(fts):
            if j not in [9]:
                continue
            with open(f"test/outputs/bulk/pdf{i}_t{j}.info", "w") as f:
                pass
            try: 
                ft.df().to_csv(f"test/outputs/bulk/pdf{i}_t{j}.csv", index=False)
            except Exception as e:
                print(f"df Error in pdf {i} and table {j}")
        doc.close()
        break

if __name__ == '__main__':
    script_collect_csvs()
