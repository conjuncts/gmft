from gmft.algorithm.structure_rewrite import (
    _tatr_predictions_to_partitions,
)
from gmft.formatters.base import FormattedTable
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.reformat._calc.polaric import (
    _set_row_col_numbers,
    _table_to_words_df,
    _words_to_table_array,
    _words_to_table_array,
)


# def test_polaric_pivot(pdf1_tables):

if __name__ == "__main__":
    from gmft.pdf_bindings.pdfium import PyPDFium2Document

    # Import for testing/script usage
    try:
        from ..conftest import get_tables_for_pdf
    except ImportError:
        # Fallback for when running as script
        import sys
        import os

        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from conftest import get_tables_for_pdf

    pdf1_tables = get_tables_for_pdf(
        docs_bulk=[PyPDFium2Document(f"data/pdfs/1.pdf")],
        n=1,  # for 1.pdf, parametrized between [0, 8]
        # the rest unneeded
        detector=None,
        formatter=None,
        tatr_tables=None,
    )
    ft: FormattedTable = pdf1_tables[1]

    partitions = _tatr_predictions_to_partitions(
        ft.predictions.bbox, TATRFormatConfig(), ft.width, ft.height
    )

    # state = partition_extract_to_state(partitions, table=ft)
    # TODO: temporarily broken

    df = _table_to_words_df(ft)
    df2 = _set_row_col_numbers(
        df, partitions.row_dividers, partitions.col_dividers
    )  # produces the warnings
    df3 = _words_to_table_array(df2)

    df4 = _words_to_table_array(df2)
    pass
