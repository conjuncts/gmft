import copy
from dataclasses import dataclass
import json

import pandas as pd
from gmft.algo.dividers import fill_using_true_partitions
from gmft.algo.histogram import IntervalHistogram
from gmft.detectors.common import CroppedTable
from gmft.formatters.common import BaseFormatter, FormattedTable
from gmft.table_visualization import plot_results_unwr, plot_shaded_boxes


@dataclass
class HistogramConfig:
    sep_line_percent_of_height: int = 0.2 # classify something as a separator line if it's 20% of the max height found in the interval histogram
    sep_line_threshold: int = 1 # 

    row_sep_threshold: int = 0
    col_sep_threshold: int = 0


class HistogramFormattedTable(FormattedTable):
    """
    A table formatted using the histogram method.
    """
    
    id2label = {
        # 0: 'table',
        1: 'column divider', # table column',
        2: 'row divider', # table row',
    }
    irvl_results: dict
    """
    irvl_results['row_dividers'] = list of row dividers, of form (y0, y1) (assumed to stretch the width of the table)\
    irvl_results['col_dividers'] = list of column dividers, of form (x0, x1) (assumed to stretch the height of the table)
    """
    def __init__(self, table: CroppedTable, df: pd.DataFrame, irvl_results, config: HistogramConfig, 
                 x_histogram: IntervalHistogram=None, y_histogram: IntervalHistogram=None):
        super().__init__(table, df)
        self.irvl_results = irvl_results
        self.config = config
        self.x_histogram = x_histogram
        """
        [Experimental] (x0, x1) intervals correspond to column dividers. It is possibly large, so by default it is not populated. To populate, 
        """
        self.y_histogram = y_histogram
        """
        [Experimental] (y0, y1) intervals correspond to row dividers. By default, it is None; 
        """
    
    def visualize(self, **kwargs):
        """
        Visualize the cropped table.
        """
        img = self.image()
        # labels = self.fctn_results['labels']
        # bboxes = self.fctn_results['boxes']
        tbl_width = self.width
        tbl_height = self.height
        
        labels = []
        bboxes = []
        for x0, x1 in self.irvl_results['col_dividers']:
            bboxes.append([x0, 0, x1, tbl_height])
            labels.append(1)
        for y0, y1 in self.irvl_results['row_dividers']:
            bboxes.append([0, y0, tbl_width, y1])
            labels.append(2)
        return plot_shaded_boxes(img, labels=labels, boxes=bboxes, **kwargs)
    
    def recompute(self):
        """
        Recalculate the table, based on irvl_results and config.
        """
        tbl_width = self.table.bbox[2] - self.table.bbox[0]
        tbl_height = self.table.bbox[3] - self.table.bbox[1]
        
        x_sep_bounds = self.irvl_results['col_dividers']
        y_sep_bounds = self.irvl_results['row_dividers']
        xavgs = [(x0 + x1) / 2 for x0, x1 in x_sep_bounds]
        yavgs = [(y0 + y1) / 2 for y0, y1 in y_sep_bounds]

        
        fix_bbox = (0, 0, tbl_width, tbl_height)
        words = list(self.table.text_positions(remove_table_offset=True))
        nparr = fill_using_true_partitions(words, yavgs, xavgs, fix_bbox)

        # simple np array
        df = pd.DataFrame(nparr[1:], columns=nparr[0])
        self._df = df
        return df

class HistogramFormatter(BaseFormatter):
    def __init__(self, config: HistogramConfig=None):
        if config is None:
            config = HistogramConfig()
        self.config = config
    
    def decide_histogram_threshold(self, histogram: IntervalHistogram, is_row: bool) -> float:
        """
        Decide a threshold for which to consider a gap to be a separator.
        This method can be overridden to provide custom logic.
        
        :param histogram: the histogram to analyze
        :param is_row: whether the histogram is for rows or columns
        :return: float: the threshold
        """
        if is_row:
            # rows are pretty robustly separated, because there tends not to be
            # text that spans 
            return self.config.row_sep_threshold # 0
        else:
            # columns are a bit trickier, because
            max_height = histogram.height
            if max_height <= 2:
                return self.config.col_sep_threshold # 0
            else:
                return self.config.col_sep_threshold # 0
                # return 1
        
    def decide_separator(self, interval: tuple[float, float], max_width: float, is_row: bool) -> bool:
        """
        Decide whether an interval is a separator.
        
        For example, it may be useful to reject vertical separators that are too thin (thinner than a space's length)
        as not a separator.
        """
        if is_row:
            return True
        width = interval[1] - interval[0]
        return width > 3
    
    def extract(self, table: CroppedTable, _populate_histograms=False) -> FormattedTable:
        """
        Take the words
        Make 2 IntervalHistograms: one for x, one for y
        separating lines are as needed
        get the means of the sep lines for stability
        done
        """
        words = list(table.text_positions(remove_table_offset=True)) # list of tuples of (text, x0, y0, x1, y1)
        x_histogram = IntervalHistogram()
        y_histogram = IntervalHistogram()
        for x0, y0, x1, y1, text in words:
            # round to 0.05
            x0 = round(x0, 2)
            x1 = round(x1, 2)
            y0 = round(y0, 2)
            y1 = round(y1, 2)
            x_histogram.append((x0, x1)) # x bounds are col separators
            y_histogram.append((y0, y1)) # y bounds are row separators
        
        x_sep_threshold = self.decide_histogram_threshold(x_histogram, is_row=False)
        x_sep_bounds = list(x_histogram.iter_intervals_below(x_sep_threshold))
        
        y_sep_threshold = self.decide_histogram_threshold(y_histogram, is_row=True)
        y_sep_bounds = list(y_histogram.iter_intervals_below(y_sep_threshold))
        # return x_sep_bounds, y_sep_bounds

        x_sep_max = max([x1 - x0 for x0, x1 in x_sep_bounds], default=None)
        y_sep_max = max([y1 - y0 for y0, y1 in y_sep_bounds], default=None)
        
        # filter out the small separators, or with custom logic
        x_sep_bounds = [(x0, x1) for x0, x1 in x_sep_bounds if self.decide_separator((x0, x1), x_sep_max, is_row=False)]
        y_sep_bounds = [(y0, y1) for y0, y1 in y_sep_bounds if self.decide_separator((y0, y1), y_sep_max, is_row=True)]
        
        irvl_results = {
            # 'labels': [],
            # 'boxes': [],
            'row_dividers': y_sep_bounds, # .append([0, y0, tbl_width, y1])
            'col_dividers': x_sep_bounds # .append([x0, 0, x1, tbl_height])
        }
        
        # compute for the first time
        tbl_width = table.width
        tbl_height = table.height
        xavgs = [(x0 + x1) / 2 for x0, x1 in x_sep_bounds]
        yavgs = [(y0 + y1) / 2 for y0, y1 in y_sep_bounds]
        fix_bbox = (0, 0, tbl_width, tbl_height)
        
        # simple np array
        nparr = fill_using_true_partitions(words, yavgs, xavgs, fix_bbox)
        df = pd.DataFrame(nparr[1:], columns=nparr[0])
        table = HistogramFormattedTable(copy.copy(table), df, irvl_results, config=self.config)
        if _populate_histograms:
            table.x_histogram = x_histogram
            table.y_histogram = y_histogram
        return table
        
