# feat: selective reocr

import os
from gmft_pymupdf import PyMuPDFPage, PyMuPDFDocument
from gmft.pdf_bindings.common import BasePage
from gmft.table_function_algorithm import _iob

import pandas as pd
import re

def load_correction_df(correction_df: pd.DataFrame, all_pdfs_for_sanity: list[str]):
    """
    From the dataframe, expect these fields:
    pdfname (str), pageno (str), ctr (str), 
    real_char (str), confidence (float), x0 (float), y0 (float), x1 (float), y1 (float)
    """
    # only get those where cls is "±" and confidence > 0.98
    correction_df = correction_df[(correction_df['real_char'] == "±") & (correction_df['confidence'] > 0.98)]

    # sanity check
    for pdfname in correction_df['pdfname']:
        if isinstance(pdfname, str):
            assert not pdfname.endswith(".pdf"), f"{pdfname} should not end with .pdf"
        assert f"{pdfname}.pdf" in all_pdfs_for_sanity, f"{pdfname}.pdf not found in the list of all pdfs"
    return correction_df

class PyMuPDFDocument_REOCR(PyMuPDFDocument):
    
    _redo_re = re.compile(r"^([ft68]|\+-)$") # change to what you need
    def __init__(self, filename: str, correction_df: pd.DataFrame):
        super().__init__(filename)
        self.filename = filename
        self.correction_df = correction_df
    
    def _correct_page(self, page: PyMuPDFPage, subset: list[tuple]):
        # monkeypatch page.get_positions_and_text
        def rectify_func(old_func):
            def result():
                for x0, y0, x1, y1, text in old_func():
                    # check if match the ± sign
                    if PyMuPDFDocument_REOCR._redo_re.search(text):
                        # check IOB
                        for rect in subset:
                            score = _iob(rect, (x0, y0, x1, y1)) 
                            # if dataframe's rect mostly covers the pdf ± rect
                            # note: this is the fraction of the pdf rect
                            if score > 0.5:
                                # print("FOUND: ", score)
                                # replace +- with ±
                                good_text = PyMuPDFDocument_REOCR._redo_re.sub("±", text)
                                yield x0, y0, x1, y1, good_text
                                break
                        else:
                            yield x0, y0, x1, y1, text # + f" ({(x0, y0, x1, y1)})"  
                    else:
                        yield x0, y0, x1, y1, text
            return result
        page.get_positions_and_text = rectify_func(page.get_positions_and_text)
            
        
    def get_page(self, n: int) -> BasePage:
        prev = super().get_page(n)
        # df has columns pdfname,pageno,ctr,real_char,x0,y0,x1,y1
        # need to match pdfname, pageno
        basename = os.path.basename(self.filename)
        if basename.endswith(".pdf"):
            basename = basename[:-4]
        good_df = self.correction_df[(self.correction_df['pdfname'] == basename) & (self.correction_df['pageno'] == n)]
        
        tuples = good_df[['x0', 'y0', 'x1', 'y1']].apply(tuple, axis=1)
        
        self._correct_page(prev, tuples)
        return prev