import polars as pl

from gmft.formatters.base import FormattedTable


def _table_to_words_df(
    ft: FormattedTable,
):
    """
    Produce the "words" DataFrame (but without row/col numbers) from the FormattedTable.
    """

    return pl.DataFrame(
        list(ft.text_positions(remove_table_offset=True)),
        schema={
            "xmin": pl.Float64,
            "ymin": pl.Float64,
            "xmax": pl.Float64,
            "ymax": pl.Float64,
            "text": pl.Utf8,
        },
        orient="row",
    )


def _set_row_col_numbers(
    words: pl.DataFrame,
    row_dividers: list[float],
    col_dividers: list[float],
) -> pl.DataFrame:
    """
    Assign row and column numbers to words based on their positions.

    Assumes that the dividers include the end bounds of the table.
    """

    num_rows = len(row_dividers) - 1
    num_columns = len(col_dividers) - 1

    column_labels = ["None", *(str(i) for i in range(num_columns)), "None"]
    row_labels = ["None", *(str(i) for i in range(num_rows)), "None"]

    # NOTE: Tested with polars v1.30 - cut() is marked as unstable.
    df = words.with_columns(
        ((pl.col("xmin") + pl.col("xmax")) / 2)
        .cut(
            breaks=col_dividers,
            labels=column_labels,
        )
        .replace("None", None)
        .alias("col_num"),
        ((pl.col("ymin") + pl.col("ymax")) / 2)
        .cut(
            breaks=row_dividers,
            labels=row_labels,
        )
        .replace("None", None)
        .alias("row_num"),
    )
    return df


def _words_to_table_array(
    words: pl.DataFrame,
) -> pl.DataFrame:
    """
    Convert words DataFrame to a 2D array of strings.

    :param words: DataFrame with columns xmin, ymin, xmax, ymax, text.
    :param row_dividers: List of y values where table gets partitioned into rows.
    :param col_dividers: List of x values where table gets partitioned into columns.
    :return: 2D list of strings representing the table.
    """

    aggregated = (
        words.lazy()
        .filter(pl.col("row_num").is_not_null() & pl.col("col_num").is_not_null())
        .group_by([pl.col("row_num"), pl.col("col_num")])
        .agg(pl.col("text"))
        .with_columns(pl.col("text").list.join(" ").alias("text"))
        .collect()
    )

    # pivot() requires eager
    return aggregated.pivot(
        index="row_num",
        on="col_num",
        values="text",
        aggregate_function="first",
    ).sort("row_num")
