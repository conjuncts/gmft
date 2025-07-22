import polars as pl
from polars.testing import assert_frame_equal

from gmft.algorithm.structure_rewrite import (
    _tatr_predictions_to_partitions,
    table_to_textbbox_list,
)
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.reformat._calc.estimate import _estimate_row_height_kmeans_all


def test_table_row_line_heights(pdf_tables):
    config = TATRFormatConfig(
        force_large_table_assumption=False,
    )
    dfs = []
    collector = []
    for i, tables in enumerate(pdf_tables):
        pdf_i = i + 1
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

    df.write_csv("data/test/outputs/df/bulk_row_heights.csv")
    expected = pl.read_csv("data/test/references/bulk_row_heights.csv")
    assert df.write_csv() == expected.write_csv()
