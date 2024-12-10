
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


@dataclass
class Consideration:
    cells: list[list[tuple[float, float, float, float]]]
    """List of cells. Each cell contains a list of words that belong in it."""



class FreeTable(FormattedTable):
    """
    FormattedTable, with the liberty to customize the partition locations.
    """

    _major_loc: PartitionLocations
    """major partition locations. These are significant, usually found deeply. """

    _minor_loc: PartitionLocations = None
    """minor partition locations. These can be line breaks, found using the histogram method. """

    x_histogram: IntervalHistogram
    """x-axis histogram. This is experimental, and can be used to visualize the x-axis intervals. """

    y_histogram: IntervalHistogram
    """y-axis histogram. This is experimental, and can be used to visualize the y-axis intervals. """

    collect_df: pl.DataFrame

    def __init__(self, table: FormattedTable, major: PartitionLocations, # minor: PartitionLocations,
                 x_histogram: IntervalHistogram=None, y_histogram: IntervalHistogram=None, 
                 words=None):
        super().__init__(table, table.df)
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

    @property
    def get_minor(self):
        if self._minor_loc is None:
            raise ValueError("Minor partition locations not set.")
        return self._minor_loc
    
    def set_minor(self, minor: PartitionLocations):
        """
        Set the minor partition locations, if they are available.
        """
        self._minor_loc = minor
    
    def with_minor_rows(self, min_partition_height: float = 0.01, 
                              min_row_height: float = 0.01, 
                              min_line_count: int = None,
                              max_frequency: float = 5):
        """
        Recalculate the minor partition locations for rows

        :param min_partition_height: the partition needs to be at least this tall, or else it gets discounted
        as a transient minima (excluded)
        :param min_row_height: the row needs to be at least this tall, or else the partition gets discounted
        :param min_line_count: the partition must have a row height of at least (min_line_count * avg_word_height). 
            If both this and min_row_height are given, then the partition must satisfy both conditions.
        :param min_density: the interval histogram must have at most <= max_frequency for a partition to be considered
        """

        if min_line_count is not None and self.avg_word_height is not None:
            min_row_height = min(min_row_height, min_line_count * self.avg_word_height)
        
        y_minima = find_local_minima(self.y_histogram.sorted_points)
        # tuples of (p, pfreq, q-p)

        acceptable = []
        for p, pfreq, q in y_minima:
            if pfreq > max_frequency:
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
    
    def split_rows(self, func: Callable[[Consideration, Consideration], bool], top_down=True):
        """
        Split the major rows, based on a function.

        Strategy: everywhere, major columns will be used.
        
        We start with the major rows, which are the words divided into rows based on 
            the major row partitions (averages).
        The major rows will be divided based on the minor rows partitions. 
        For each row: split 
        The function: f(minor_row, the_rest) should decide if a partition should stay.
        Then, the_rest will be split into minor_row and the_rest, and the process will repeat.
        """
        pass

    def collect(self) -> pl.DataFrame:
        """
        Collect the data into a DataFrame.
        """
        
        # polars's cut method
        x_cut_locs = []
        for x0, x1 in self._major_loc.col_dividers:
            x_cut_locs.append((x0 + x1) / 2)
        
        y_cut_locs = []
        for y0, y1 in self._major_loc.row_dividers:
            y_cut_locs.append((y0 + y1) / 2)
        
        x_labels = [str(x) for x in range(len(x_cut_locs) + 1)]
        y_labels = [str(x) for x in range(len(y_cut_locs) + 1)]

        self.words_df = self.words_df.with_columns([
            ((pl.col("x0") + pl.col("x1")) / 2).alias("xavg"),
            ((pl.col("y0") + pl.col("y1")) / 2).alias("yavg")
        ]).with_columns([
            pl.col("xavg").cut(x_cut_locs, labels=x_labels, left_closed=True).alias("col_idx"),
            pl.col("yavg").cut(y_cut_locs, labels=y_labels, left_closed=True).alias("row_idx")
        ])

        self.collect_df = self.words_df.group_by(["row_idx", "col_idx"]).agg([
            pl.col("text")
        ]).with_columns([
            pl.col("text").list.join(" ").alias("text"), # joined_text")
            pl.col("row_idx").cast(pl.Int32),
            pl.col("col_idx").cast(pl.Int32)
        ])

        # convert to a DataFrame
        _df = self.collect_df.pivot(on="col_idx", values="text").sort("row_idx").select([
            pl.col("row_idx"), 
            *[pl.col(x) for x in x_labels]
        ])
        return _df


_global_formatter = HistogramFormatter()

from gmft.formatters.tatr import TATRFormattedTable
def _convert(ft: FormattedTable):
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
    with open("test/refs/tatr_tables.json") as f:
        tatr_tables = json.load(f)
    
    for key in tatr_tables:
        # print(key)
        # ft, doc = presets.load_tatr_formatted_table(tatr_tables["pdf1_t0"])
        ft, doc = presets.load_tatr_formatted_table(tatr_tables[key])
        ftable = _convert(ft)
        out = ftable.collect()
        print(out)
        doc.close()