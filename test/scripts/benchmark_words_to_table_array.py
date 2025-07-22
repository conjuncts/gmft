from typing import List
from gmft.algorithm.dividers import find_column_for_target, find_row_for_target
from gmft.pdf_bindings.pdfium import PyPDFium2Document
from gmft.formatters.base import FormattedTable
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.algorithm.structure_rewrite import (
    _tatr_predictions_to_partitions,
    table_to_textbbox_list,
)
from gmft.reformat._calc.estimate import _estimate_row_height_kmeans_all
from gmft.reformat._calc.polaric import (
    _set_row_col_numbers,
    _table_to_words_df,
    _words_to_table_array,
    _words_to_table_array_polars,
)
import timeit

import polars as pl

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


from gmft_pymupdf import PyMuPDFDocument


def prepare_tables(pdf_n=1) -> List[FormattedTable]:
    docs_bulk = [None] * (pdf_n)
    docs_bulk[-1] = PyPDFium2Document(f"data/pdfs/{pdf_n}.pdf")

    # docs_bulk[-1] = PyMuPDFDocument(f"data/pdfs/{pdf_n}.pdf")
    return get_tables_for_pdf(
        docs_bulk=docs_bulk,
        n=pdf_n,
        detector=None,
        formatter=None,
        tatr_tables=None,
    )


def prepare_ft(pdf_n=1, n=1) -> FormattedTable:
    return prepare_tables(pdf_n=pdf_n)[n]


def benchmark_words_to_table_array():
    ft = prepare_ft(n=2)
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

    print(f"_words_to_table_array: {time_array / num_runs:.6f} seconds per run")
    print(
        f"_words_to_table_array_for_loop: {time_for_loop / num_runs:.6f} seconds per run"
    )


def for_loop_words_with_row_col(ft, row_dividers, col_dividers):
    # Step 1: Get the words as a list of dicts
    words = []
    for xmin, ymin, xmax, ymax, text in ft.text_positions(remove_table_offset=True):
        x_center = (xmin + xmax) / 2
        y_center = (ymin + ymax) / 2

        # Find which bin the center falls into
        col_idx = None
        for i in range(len(col_dividers) - 1):
            if col_dividers[i] <= x_center < col_dividers[i + 1]:
                col_idx = i
                break

        row_idx = None
        for i in range(len(row_dividers) - 1):
            if row_dividers[i] <= y_center < row_dividers[i + 1]:
                row_idx = i
                break

        words.append(
            {
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
                "text": text,
                "row_idx": row_idx,
                "col_idx": col_idx,
            }
        )

    return words


def for_loop_words_with_row_col_binsearch(ft, row_dividers, col_dividers):
    return table_to_textbbox_list(ft, row_dividers, col_dividers)


def benchmark_for_loop_words_with_row_col():
    # for loop binsearch: 0.000492 seconds per run
    # for loop: 0.000503 seconds per run
    # polars: 0.000763 seconds per run

    # Even for a pretty small table, binsearch is still comparable to better
    # Data is too small for polars to be faster

    ft = prepare_ft(n=0)
    num_runs = 1000

    partitions = _tatr_predictions_to_partitions(
        ft.predictions.bbox, TATRFormatConfig(), ft.width, ft.height
    )

    def run_polars():
        df = _table_to_words_df(ft)
        df2 = _set_row_col_numbers(df, partitions.row_dividers, partitions.col_dividers)

    def run_for_loop():
        for_loop_words_with_row_col(
            ft, partitions.row_dividers, partitions.col_dividers
        )

    def run_for_loop_binsearch():
        for_loop_words_with_row_col_binsearch(
            ft, partitions.row_dividers, partitions.col_dividers
        )

    time_polars = timeit.timeit(run_polars, number=1)

    time_polars = timeit.timeit(run_polars, number=num_runs)
    time_for_loop = timeit.timeit(run_for_loop, number=num_runs)
    time_for_loop_binsearch = timeit.timeit(run_for_loop_binsearch, number=num_runs)

    print(f"for loop: {time_for_loop / num_runs:.6f} seconds per run")
    print(f"polars: {time_polars / num_runs:.6f} seconds per run")
    print(
        f"for loop binsearch: {time_for_loop_binsearch / num_runs:.6f} seconds per run"
    )


def benchmark_table_row_line_heights():
    config = TATRFormatConfig(
        force_large_table_assumption=False,
    )
    dfs = []
    collector = []
    for pdf_i in range(1, 9):
        # for pdf_i in [1]:
        tables = prepare_tables(pdf_i)
        for table_i, ft in enumerate(tables):
            partitions = _tatr_predictions_to_partitions(
                ft.predictions.bbox,
                config,
                ft.width,
                ft.height,
                word_height=ft.predicted_word_height(),
            )
            words_list = table_to_textbbox_list(
                ft, partitions.row_dividers, partitions.col_dividers
            )

            results = _estimate_row_height_kmeans_all(words_list)
            # for row_i, row_h in results.items():
            #     collector.append({
            #         'pdf': pdf_i,
            #         'table_i': table_i,
            #         'row_i': row_i,
            #         'row_height': row_h
            #     })

            # disable large table assumption
            my_df = ft.to_pandas(config=config)
            collector.append(
                {
                    "pdf": pdf_i,
                    "table_i": table_i,
                    "row_heights": " ".join([str(x) for x in results.values()]),
                }
            )
            dfs.append(my_df)

    df = pl.DataFrame(collector)
    print(df)

    df.write_csv("data/test/references/bulk_row_heights.csv")


if __name__ == "__main__":
    # benchmark_for_loop_words_with_row_col()
    benchmark_table_row_line_heights()
