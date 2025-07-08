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
        .cast(pl.Int64, strict=False) # strict=False turns "None" -> None
        .alias("col_num"),
        ((pl.col("ymin") + pl.col("ymax")) / 2)
        .cut(
            breaks=row_dividers,
            labels=row_labels,
        )
        .cast(pl.Int64, strict=False) # strict=False turns "None" -> None
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



def _words_to_table_array_polars(
    words: pl.DataFrame,
) -> pl.DataFrame:
    """
    Convert words DataFrame to a 2D array of strings.
    
    Below is a polars-only version, but it's slower than for loop.
    I suspect because the polars "pivot()" must generalize to arbitrary number of rows/columns
    while we have a special case where we can exactly allocate the table size

    :param words: DataFrame with columns xmin, ymin, xmax, ymax, text, row_num, col_num.
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
    df = aggregated.pivot(
        index="row_num",
        on="col_num",
        values="text",
        aggregate_function="first",
    ).sort("row_num")

    # rearrange columns
    has_columns = df.columns[1:]  # skip row_num
    sorted_columns = sorted(has_columns, key=lambda x: int(x) if x.isdigit() else float('inf'))
    df = df.select([pl.col("row_num")] + [pl.col(c) for c in sorted_columns])
    return df

def _words_to_table_array(
    words: pl.DataFrame,
) -> pl.DataFrame:
    """
    Convert words DataFrame to a 2D array of strings.

    Uses non-parallel for loop for benchmarking purposes.

    :param words: DataFrame with columns xmin, ymin, xmax, ymax, text, row_num, col_num.
    :return: 2D list of strings representing the table.
    """

    row_count = words["row_num"].max() + 1
    col_count = words["col_num"].max() + 1

    table = [[None] * col_count for _ in range(row_count)]

    for text, row_num, col_num in words.select(["text", "row_num", "col_num"]).iter_rows():
        if row_num is not None and col_num is not None:
            if table[row_num][col_num] is None:
                table[row_num][col_num] = text
            else:
                table[row_num][col_num] += " " + text
    
    # Convert to DataFrame
    return (
        pl.DataFrame(table, schema={f"{i}": pl.Utf8 for i in range(col_count)}, orient="row")
        .with_row_index("row_num")
    )