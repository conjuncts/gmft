
import copy
from dataclasses import dataclass
from typing import Callable
import polars as pl
from gmft.algo.dividers import convert_cells_to_dividers
from gmft.algo.histogram import IntervalHistogram
from gmft.algo.minima import find_local_minima
from gmft.algo.table_function_algorithm import TATRLocations
from gmft.formatters.common import FormattedTable, PartitionLocations
from gmft.formatters.histogram import HistogramFormatter, _populate_histogram_func



def obtain_partition_locations(tatr_locations: TATRLocations) -> PartitionLocations:
    """
    Given the results of the TATR algorithm, extract the partition locations.
    """
    # need to convert effective_rows into list of partitions

    # use gmft.algo.dividers.convert_cells_to_dividers

    horiz_cells = [(x['bbox'][1], x['bbox'][3]) for x in tatr_locations.effective_rows]
    # vert_cells = [(x0, x1) for x0, _, x1, _ in tatr_locations.effective_columns]
    vert_cells = [(x['bbox'][0], x['bbox'][2]) for x in tatr_locations.effective_columns]

    horiz_dividers = convert_cells_to_dividers(horiz_cells)
    vert_dividers = convert_cells_to_dividers(vert_cells)

    return PartitionLocations(
        table_bbox=tatr_locations.table_bbox, 
        row_dividers=horiz_dividers, 
        col_dividers=vert_dividers,
        top_header_indices=tatr_locations.top_header_indices,
        projecting_indices=tatr_locations.projecting_indices,
        left_header_indices=tatr_locations.left_header_indices
    )


def _divider_averages(dividers):
    """return divider averages"""
    x_cut_locs = []
    for x0, x1 in dividers: # self._major_loc.col_dividers:
        if x1 is None:
            continue
        x_cut_locs.append((x0 + x1) / 2)
    return x_cut_locs
    
    # x_labels = [str(x) for x in range(len(x_cut_locs) + 1)]

@dataclass
class Consideration:
    cells: list[list[tuple[float, float, float, float]]]
    """List of cells. Each cell contains a list of words that belong in it."""



class FreeTable:
    """
    FormattedTable, with the liberty to customize the partition locations.
    """

    # Note: this class should be treated as immutable. words_df and collect_df are 
    # and populated as needed and hence mutated by assign_cells() and collect().
    # but they are ultimately derived quantities based on partition locations. 
    # if partition locations needs to be changed, then a new copy should be made.

    _major_loc: PartitionLocations
    """major partition locations. These are significant, usually found deeply. """

    _minor_loc: PartitionLocations = None
    """minor partition locations. These can be line breaks, found using the histogram method. """

    x_histogram: IntervalHistogram
    """x-axis histogram. This is experimental, and can be used to visualize the x-axis intervals. """

    y_histogram: IntervalHistogram
    """y-axis histogram. This is experimental, and can be used to visualize the y-axis intervals. """

    # tabulated_df: pl.DataFrame = None
    is_cells_assigned = False
    collect_df: pl.DataFrame = None

    def __init__(self, table: FormattedTable, major: PartitionLocations, # minor: PartitionLocations,
                 x_histogram: IntervalHistogram=None, y_histogram: IntervalHistogram=None, 
                 words=None, custom_initialization=False):
        # super().__init__(table, table.df)
        if custom_initialization:
            return
        self._ft = table
        self._major_loc = major
        self._minor_loc = copy.copy(major)
        # self._minor_loc = minor

        self.x_histogram = x_histogram
        self.y_histogram = y_histogram

        if words is None:
            words = list(table.text_positions(remove_table_offset=True))
        # self.words = words

        self.words_df = (
            pl.DataFrame(words, schema=["x0", "y0", "x1", "y1", "text"], orient='row')
            .with_row_index("word_index")
        )

        # self.avg_word_height = sum(y1 - y0 for x0, y0, x1, y1, _ in words) / len(words)
        self.avg_word_height = self.words_df.select(pl.col("y1") - pl.col("y0")).mean().item()

    def clone(self):
        et = FreeTable(None, None, custom_initialization=True)
        et._ft = self._ft
        et._major_loc = copy.copy(self._major_loc)
        et._minor_loc = copy.copy(self._minor_loc)
        et.x_histogram = copy.copy(self.x_histogram)
        et.y_histogram = copy.copy(self.y_histogram)
        et.words_df = self.words_df.clone()
        et.avg_word_height = self.avg_word_height
        et.is_cells_assigned = self.is_cells_assigned
        et.collect_df = self.collect_df.clone() if self.collect_df is not None else None
        return et
    
    @property
    def get_minor(self):
        if self._minor_loc is None:
            raise ValueError("Minor partition locations not set.")
        return self._minor_loc
    
    
    def with_table_bbox(self, table_bbox, rotated=None) -> 'FreeTable':
        """
        Change the table bounding box.
        Relatively expensive;
        Recalculates the words_df and the histograms.
        """
        raise NotImplementedError
    
    def adjust_table_bbox(self, dtable_bbox) -> 'FreeTable':
        """
        Move the table bounding box.
        """
        raise NotImplementedError
    
    def with_minor_rows(self, min_partition_height: float = 0.01, 
                              min_row_height: float = 0.01, 
                              min_line_count: int = None,
                              max_density: float = 10) -> 'FreeTable':
        """
        Recalculate the minor partition locations for rows

        :param min_partition_height: the partition needs to be at least this tall, or else it gets discounted
        as a transient minima (excluded)
        :param min_row_height: the row needs to be at least this tall, or else the partition gets discounted
        :param min_line_count: the partition must have a row height of at least (min_line_count * avg_word_height). 
            If both this and min_row_height are given, then the partition must satisfy both conditions.
        :param max_density: the interval histogram's frequency must be at most <= max_density for a partition to be considered
        """

        self = self.clone()

        if min_line_count is not None and self.avg_word_height is not None:
            min_row_height = min(min_row_height, min_line_count * self.avg_word_height)
        
        y_minima = find_local_minima(self.y_histogram.sorted_points)
        # tuples of (p, pfreq, q-p)

        acceptable = []
        for p, pfreq, q in y_minima:
            if max_density is not None and pfreq > max_density:
                continue

            if q is not None:
                height = q - p
                if height < min_partition_height:
                    continue
            
            # now compare against the previous partition, to calculate row height.
            if acceptable:
                _, lastq = acceptable[-1]
                if p - lastq < min_partition_height:
                    continue                
            
            acceptable.append((p, q))
        
        self._minor_loc.row_dividers = acceptable
        return self
    
    def subdivide_rows_when(self, decision_func: Callable[[pl.DataFrame], bool], top_down=True) -> 'FreeTable':
        """
        Conditionally split the (bigger) major row cells with the minor partitions.

        In other words, subdivide the major rows using the minor rows.

        We always only look at one major row at a time. 
        The decision function is given a DataFrame of exactly two rows. We consider only 1 subdivision at a time.
        The df.row(0) is a smaller row that we can potentially split off. 
        df.row(1) is the rest of the major row.

        The decision function should return True if the row should be split that way, and False if we decide to keep the rows together.

        The process is repeated until we consider every subdivision.
        """
        if not self.is_cells_assigned:
            self.assign_cells()
        self = self.clone()
        # mapping of row_idx to minor_row_idx
        minor_row_df = et.words_df.group_by('row_idx').agg([
            pl.col('minor_row_idx').unique().sort()
        ])
        
        unnecessary_partitions = []

        # iterate through the major rows
        for major_row, minor_rows in minor_row_df.iter_rows():
            # pass
            # prepare the decision_df
            candidates = list(minor_rows)
            if not top_down:
                candidates = candidates[::-1]

            bottom_subset = self.words_df.filter(
                pl.col("row_idx") == major_row
            )
            top_subset = bottom_subset.clear() # empty DataFrame with same columns. AKA .head(0)
            # single out one row at a time

            for i, top_row_idx in enumerate(candidates[:-1]):
                # i is the position of the top row
                top_content = bottom_subset.filter(pl.col("minor_row_idx") == top_row_idx)
                bottom_subset = bottom_subset.filter(pl.col("minor_row_idx") != top_row_idx)

                top_content = top_subset.merge_sorted(
                    top_content, 
                    'word_index'
                ) # maintain reading order. merge sorted is an O(n) operation, making n loops of this O(n^2).

                # now we have the top and bottom rows
                top_df = _words_to_dfs(top_content)[0]
                bottom_df = _words_to_dfs(bottom_subset)[0]
                decision_df = pl.concat([top_df, bottom_df], how='diagonal')
                decision_df = _reorder_columns(decision_df)
                # print(decision_df)

                if decision_func(decision_df):
                    # split the row
                    # hence we no longer need the top content
                    top_subset = top_subset.clear()
                    # (bottom row is still good)
                else:
                    # we need to keep the top row
                    top_subset = top_content
                    # hence we merge the rows of [top_row_idx, ..., adj_row_idx := candidates[i+1]]
                    # these correspond to the partitions [top_row_idx, ..., adj_row_idx-1]
                    adj_row_idx = candidates[i+1]
                    for row_idx in range(top_row_idx, adj_row_idx):
                        unnecessary_partitions.append(row_idx)

        # nice. now we have a list of unnecessary partitions.
        # we can now remove them from the minor_row_df
        row_dividers = [
            item for i, item in enumerate(self._minor_loc.row_dividers) if i not in unnecessary_partitions
        ]
        self._major_loc.row_dividers = row_dividers
        self.is_cells_assigned = False
        return self

    def demote_major_rows(self) -> 'FreeTable':
        """
        Make the major partitions the minor partitions.

        Makes way for a new set of major partitions. (ie. if you wish to join the minor partitions)
        """
        self = self.clone()
        self._minor_loc.row_dividers = self._major_loc.row_dividers
        return self

    def promote_minor_rows(self) -> 'FreeTable':
        """
        Make the minor partitions the major partitions.

        Makes way for a new set of minor partitions.
        """
        self = self.clone()
        self._major_loc.row_dividers = self._minor_loc.row_dividers
        return self


    def assign_cells(self) -> pl.DataFrame:
        """
        Annotate positional

        This finalizes whatever the "major" and "minor" partitions are, and assigns each word to a cell.

        The 2nd to last step in turning a table into a DataFrame.
        """
        
        # polars's cut method
        x_cut_locs = _divider_averages(self._major_loc.col_dividers)
        y_cut_locs = _divider_averages(self._major_loc.row_dividers)
        x_labels = [str(x) for x in range(len(x_cut_locs) + 1)]
        y_labels = [str(x) for x in range(len(y_cut_locs) + 1)]

        minor_x_cut_locs = _divider_averages(self._minor_loc.col_dividers)
        minor_y_cut_locs = _divider_averages(self._minor_loc.row_dividers)
        minor_x_labels = [str(x) for x in range(len(minor_x_cut_locs) + 1)]
        minor_y_labels = [str(x) for x in range(len(minor_y_cut_locs) + 1)]

        self.words_df = self.words_df.with_columns([
            ((pl.col("x0") + pl.col("x1")) / 2).alias("xavg"),
            ((pl.col("y0") + pl.col("y1")) / 2).alias("yavg")
        ]).with_columns([
            pl.col("xavg").cut(x_cut_locs, labels=x_labels, left_closed=True).cast(pl.UInt32).alias("col_idx"),
            pl.col("yavg").cut(y_cut_locs, labels=y_labels, left_closed=True).cast(pl.UInt32).alias("row_idx"),
            pl.col("xavg").cut(minor_x_cut_locs, labels=minor_x_labels, left_closed=True).cast(pl.UInt32).alias("minor_col_idx"),
            pl.col("yavg").cut(minor_y_cut_locs, labels=minor_y_labels, left_closed=True).cast(pl.UInt32).alias("minor_row_idx")
        ])
        self.is_cells_assigned = True
        return self.words_df

    def collect(self) -> pl.DataFrame:
        """
        Collect the data into a DataFrame.

        The final step in turning a table into a DataFrame.
        """

        if not self.is_cells_assigned:
            self.assign_cells()
        
        _df, collect_df = _words_to_dfs(self.words_df)
        self.collect_df = collect_df
        return _df

def _reorder_columns(df):
    present_columns = list(df.columns)
    present_columns.sort(key=lambda x: -1 if x == 'row_idx' else int(x))
    df = df.select([
        *present_columns
    ])
    return df

def _words_to_dfs(words_df):
    collect_df = words_df.group_by(["row_idx", "col_idx"]).agg([
        pl.col("text")
    ])
    if collect_df.is_empty():
        return pl.DataFrame()
    collect_df = collect_df.with_columns([
        pl.col("text").list.join(" ").alias("text"), # joined_text")
        pl.col("row_idx").cast(pl.Int32),
        pl.col("col_idx").cast(pl.Int32)
    ])
    # self.collect_df = collect_df

    # convert to a DataFrame
    _df = collect_df.pivot(on="col_idx", values="text").sort("row_idx")

    _df = _reorder_columns(_df)
    return _df, collect_df

_global_formatter = HistogramFormatter()

from gmft.formatters.tatr import TATRFormattedTable
def convert_to_editable(ft: FormattedTable):
    if isinstance(ft, TATRFormattedTable):
        major = obtain_partition_locations(ft.tatr_locations)

        # mft = _global_formatter.extract(ft, _populate_histograms=True)
        # minor = mft.partition_locations

        words = list(ft.text_positions(remove_table_offset=True))
        x_histogram, y_histogram = _populate_histogram_func(ft, words)

        # x_minima = find_local_minima(x_histogram.sorted_points)
        # y_minima = find_local_minima(y_histogram.sorted_points)

        return FreeTable(ft, major, x_histogram=x_histogram, y_histogram=y_histogram, words=words)

if __name__ == "__main__":
    import json
    from gmft_pymupdf import PyMuPDFDocument

    from gmft import presets
    from gmft.formatters.tatr import TATRFormatConfig
    # with open("test/refs/tatr_tables.json") as f:
    with open("test/refs/nmr_results.json") as f:
        tatr_tables = json.load(f)
    

    config = TATRFormatConfig(force_large_table_assumption=False)
    for key in ['nmr6']: # tatr_tables:
        print(key)
        # ft, doc = presets.load_tatr_formatted_table(tatr_tables["pdf1_t0"])
        ft, doc = presets.load_tatr_formatted_table(tatr_tables[key])
        ft.recompute(config)

        et = (
            convert_to_editable(ft)
            .with_minor_rows()
            # .promote_minor_rows()
        )
        out = et.collect()

        # et2 = et.subdivide_rows_when(lambda df: True)
        def _when(df):
            if '1' in df.columns:
                val = df['1'].item(0)
                if val and val.strip() == 'CH3':
                    print(f"Pruned: {df.get_column('0', default=None).item(0)}")
                    return False
            return True
        
        et2 = et.subdivide_rows_when(lambda df: True) # always subdivide

        # et2 = et.subdivide_rows_when(_when) # always subdivide, unless CH3 (for testing) (seems to work)
        out2 = et2.collect()
        with pl.Config(tbl_rows=-1, tbl_cols=-1):
            print("Original: ")
            print(out.fill_null(""))
            print("Subdivided: ")
            print(out2.fill_null(""))
        doc.close()