import polars as pl
from polars.testing import assert_frame_equal
import pytest


def _to_df(tuples) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "x0": tup[0],
                "y0": tup[1],
                "x1": tup[2],
                "y1": tup[3],
                "text": tup[4],
                "block_idx": tup[5],
                "line_idx": tup[6],
                "word_idx": tup[7],
                **(tup[8] if len(tup) > 8 else {}),
            }
            for tup in tuples
        ]
    )


@pytest.mark.skip(reason="Slow")
def test_pdfium_words(docs_bulk):
    dfs = []
    for i, pdf in enumerate(docs_bulk):
        pdf_no = i + 1
        for page_no, page in enumerate(pdf):
            # words_df = _to_df(page._get_positions_and_text_and_breaks())
            words_df = _to_df(page._get_text_with_metadata())
            ident = f"pdf{pdf_no}_page{page_no + 1}"
            words_df = words_df.with_columns(pl.lit(ident).alias("src"))
            dfs.append(words_df)

    all_words_df = pl.concat(dfs)

    # Setup
    # all_words_df.write_csv(f'data/test/references/df/bulk_words.tsv', separator="\t")
    # all_words_df.write_parquet(f'data/test/references/df/bulk_words.parquet')

    # Compare
    all_words_df.write_parquet("data/test/outputs/df/bulk_words.parquet")
    reference = pl.read_parquet(f"data/test/references/df/bulk_words.parquet")
    assert_frame_equal(all_words_df, reference)
