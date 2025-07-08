from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.formatters.base import FormattedTable
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.algorithm.rewrite import _tatr_predictions_to_partitions
from gmft.reformat.step.polaric import (
    _set_row_col_numbers,
    _table_to_words_df,
    _words_to_table_array,
    _words_to_table_array_polars,
)
import timeit

# Import for testing/script usage
try:
    from ..conftest import get_tables_for_pdf
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from conftest import get_tables_for_pdf

def prepare_df2(ft: FormattedTable):
    partitions = _tatr_predictions_to_partitions(
        ft.predictions.bbox, TATRFormatConfig(), ft.width, ft.height
    )
    df = _table_to_words_df(ft)
    df2 = _set_row_col_numbers(df, partitions.row_dividers, partitions.col_dividers)
    return df2

def prepare_ft() -> FormattedTable:
    pdf1_tables = get_tables_for_pdf(
        docs_bulk=[PyPDFium2Document("data/pdfs/1.pdf")],
        n=1,
        detector=None,
        formatter=None,
        tatr_tables=None,
    )
    ft: FormattedTable = pdf1_tables[1]
    return ft

def benchmark_words_to_table_array():
    ft = prepare_ft()
    df2 = prepare_df2(ft)
    num_runs = 1000
    
    # _words_to_table_array: 0.000736 seconds per run
    # _words_to_table_array_for_loop: 0.000120 seconds per run
    
    # for loop is faster, even with polars parallelization

    def run_words_to_table_array():
        _words_to_table_array_polars(df2)

    def run_words_to_table_array_for_loop():
        _words_to_table_array(df2)

    time_array = timeit.timeit(run_words_to_table_array, number=num_runs)
    time_for_loop = timeit.timeit(run_words_to_table_array_for_loop, number=num_runs)

    print(f"_words_to_table_array: {time_array/num_runs:.6f} seconds per run")
    print(f"_words_to_table_array_for_loop: {time_for_loop/num_runs:.6f} seconds per run")


def for_loop_words_with_row_col(ft, row_dividers, col_dividers):
    # Step 1: Get the words as a list of dicts
    words = []
    for xmin, ymin, xmax, ymax, text in ft.text_positions(remove_table_offset=True):
        x_center = (xmin + xmax) / 2
        y_center = (ymin + ymax) / 2

        # Find which bin the center falls into
        col_num = None
        for i in range(len(col_dividers) - 1):
            if col_dividers[i] <= x_center < col_dividers[i + 1]:
                col_num = i
                break

        row_num = None
        for i in range(len(row_dividers) - 1):
            if row_dividers[i] <= y_center < row_dividers[i + 1]:
                row_num = i
                break

        words.append({
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax,
            "text": text,
            "row_num": row_num,
            "col_num": col_num,
        })

    return words

def benchmark_for_loop_words_with_row_col():
    
    # for loop: 0.000516 seconds per run
    # polars: 0.000838 seconds per run
    
    # for loop is faster, even with polars parallelization
    
    ft = prepare_ft()
    num_runs = 10000
    
    partitions = _tatr_predictions_to_partitions(
        ft.predictions.bbox, TATRFormatConfig(), ft.width, ft.height
    )

    def run_polars():
        df = _table_to_words_df(ft)
        df2 = _set_row_col_numbers(df, partitions.row_dividers, partitions.col_dividers)

    def run_for_loop():
        for_loop_words_with_row_col(ft, partitions.row_dividers, partitions.col_dividers)

    time_polars = timeit.timeit(run_polars, number=num_runs)
    time_for_loop = timeit.timeit(run_for_loop, number=num_runs)


    print(f"for loop: {time_for_loop/num_runs:.6f} seconds per run")
    print(f"polars: {time_polars/num_runs:.6f} seconds per run")

if __name__ == "__main__":
    benchmark_for_loop_words_with_row_col() 