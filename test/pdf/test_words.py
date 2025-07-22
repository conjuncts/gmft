import polars as pl
from polars.testing import assert_frame_equal
import pytest


def _to_df(tuples) -> pl.DataFrame:
    collector = []
    for tup in tuples:
        obj = {
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
        obj.pop("hyphen_parts", None)
        collector.append(obj)
    return pl.DataFrame(collector)


def _assert_frames_equal(
    df1: pl.DataFrame,
    df2: pl.DataFrame,
):
    # assert_frame_equal for debug

    common_columns = list(set(df1.columns) & set(df2.columns))
    left_only = df1.join(df2, on=common_columns, how="anti")
    right_only = df2.join(df1, on=common_columns, how="anti")
    if left_only.height > 0:
        print("Left only (actual):")
        print(left_only)
    if right_only.height > 0:
        print("Right only (expected):")
        print(right_only)
    assert_frame_equal(df1, df2, check_dtype=False, check_column_order=False)


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
    _assert_frames_equal(all_words_df, reference)
