"""
Module containing methods of formatting tables: structural analysis, data extraction, and converting them into pandas dataframes.

Whenever possible, classes (like :class:`AutoTableFormatter`) should be imported from the top-level module, not from this module,
as the exact paths may change in future versions.

Example:
    >>> from gmft import AutoTableFormatter
"""


from abc import ABC, abstractmethod
import bisect
import copy
from math import ceil
from typing import Generator

from gmft.pdf_bindings.common import BasePage
import numpy as np
import torch

from gmft.table_detection import CroppedTable, RotatedCroppedTable, TableDetectorConfig

import transformers
from transformers import AutoImageProcessor, TableTransformerForObjectDetection
import pandas as pd

from gmft.common import Rect
from gmft.table_visualization import plot_results_unwr

def _iob(bbox1: tuple[float, float, float, float], bbox2: tuple[float, float, float, float]):
    """
    Compute the intersection area over box area, for bbox1.
    """
    intersection = Rect(bbox1).intersect(bbox2)
    
    bbox1_area = Rect(bbox1).area
    if bbox1_area > 0:
        return intersection.area / bbox1_area
    
    return 0

def _symmetric_iob(bbox1, bbox2):
    """
    Compute the intersection area over box area, for min of bbox1 and bbox2
    """
    intersection = Rect(bbox1).intersect(bbox2)
    
    bbox1_area = Rect(bbox1).area
    bbox2_area = Rect(bbox2).area
    if bbox1_area > 0 and bbox2_area > 0:
        return intersection.area / min(bbox1_area, bbox2_area)
    
    return 0

class FormattedTable(RotatedCroppedTable):
    """
    This is a table that is "formatted", which is to say it is functionalized with header and data information through structural analysis.
    Therefore, it can be converted into df, csv, etc.
    """
    
    
    def __init__(self, cropped_table: CroppedTable, df: pd.DataFrame=None):
        self._df = df
        
        # create shallow copy
        if 'angle' in cropped_table.__dict__:
            angle = cropped_table.angle
        else:
            angle = 0
        super().__init__(page=cropped_table.page, 
                         bbox=cropped_table.rect.bbox, 
                         confidence_score=cropped_table.confidence_score, 
                         angle=angle,
                         label=cropped_table.label)
        # self.page = cropped_table.page
        # self.rect = cropped_table.rect
        # self.bbox = cropped_table.bbox
        # self.confidence_score = cropped_table.confidence_score
        # self.label = cropped_table.label
        
        self._img = cropped_table._img.copy() if cropped_table._img is not None else None
        self._img_dpi = cropped_table._img_dpi
        self._img_padding = cropped_table._img_padding
    
    
    
    def df(self):
        """
        Return the table as a pandas dataframe.
        """
        return self._df
    
    @abstractmethod
    def visualize(self):
        """
        Visualize the table.
        """
        raise NotImplementedError
    
    @abstractmethod
    def to_dict(self):
        """
        Serialize self into dict
        """
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize from dict
        """
        raise NotImplementedError




class TableFormatter(ABC):
    """
    Abstract class for converting a :class:`~gmft.CroppedTable` to a :class:`~gmft.FormattedTable`.
    Allows export to csv, df, etc.
    """
    
    @abstractmethod
    def extract(self, table: CroppedTable) -> FormattedTable:
        """
        Extract the data from the table.
        Produces a :class:`~gmft.FormattedTable` instance, from which data can be exported in csv, html, etc.
        """
        raise NotImplementedError

def _find_rightmost_le(sorted_list, value, key_func):
    """Find rightmost value less than or equal to value
    Therefore, finds the rightmost box where box_min <= y1
    """
    i = bisect.bisect_right(sorted_list, value, key=key_func)
    if i:
        return i-1
    # raise ValueError
    return None

def _find_leftmost_gt(sorted_list, value, key_func):
    """Find leftmost value greater than value
    Therefore, finds the leftmost box where box_max > y_min
    
    In other words, the first row where the row might intersect y_min, even a little bit
    """
    i = bisect.bisect_left(sorted_list, value, key=key_func)
    # if i < len(sorted_list):
    return i
    # return None



class TATRFormatConfig:
    """
    Configuration for :class:`~gmft.TATRTableFormatter`.
    """
    
    # ---- model settings ----
    
    warn_uninitialized_weights: bool = False
    image_processor_path: str = "microsoft/table-transformer-detection"
    formatter_path: str = "microsoft/table-transformer-structure-recognition"
    

    formatter_base_threshold: float = 0.3
    """Base threshold for the confidence demanded of a table feature (row/column).
    Note that a low threshold is actually better, because overzealous rows means that
    generally, numbers are still aligned and there are just many empty rows
    (having fewer rows than expected merges cells, which is bad).
    """
    

    cell_required_confidence = {
        0: 0.3, 
        1: 0.3, 
        2: 0.3, 
        3: 0.3, 
        4: 0.3, 
        5: 0.3,
        6: 99
    }
    """Confidences required (>=) for a row/column feature to be considered good. See TATRFormattedTable.id2label
    
    But low confidences may be better than too high confidence (see formatter_base_threshold)
    """
    
    # ---- df() settings ----
    
    large_table_threshold = 20
    """with large tables, table transformer struggles with placing too many overlapping rows
    luckily, with more rows, we have more info on the usual size of text, which we can use to make
    a guess on the height such that no rows are merged or overlapping
    
    large table assumption is only applied when (# of rows > 20) AND (total overlap > 20%)
    set 9999 to disable, set 0 to force large table assumption to run every time"""
    large_table_row_overlap_threshold = 0.2


    total_overlap_reject_threshold = 0.2
    """reject if total overlap is > 20% of table area"""
    
    total_overlap_warn_threshold = 0.05
    """warn if total overlap is > 5% of table area"""
    
    corner_clip_outlier_threshold = 0.1
    """"corner clip" is when the text is clipped by a corner, and not an edge"""
    
    iob_reject_threshold = 0.05
    """reject if iob between textbox and cell is < 5%"""

    iob_warn_threshold = 0.5
    """warn if iob between textbox and cell is < 50%"""

    remove_null_rows = True 
    """remove rows with no text"""
    
    spanning_cell_minimum_width = 0.6
    """Prunes spanning cells that are < 60% of the table width.
    Set to 0 to keep all spanning cells."""
    

    deduplication_iob_threshold = 0.95
    """iob threshold for deduplication
    if 2 consecutive rows have iob > 0.95, then one of them gets deleted (!)"""
    
    
    aggregate_spanning_cells = False
    """TATR seems to have a high spanning cell false positive rate. 
    (spanning cell or projected row header)
    That is, it identifies a regular row with information (ie. Retired|5|3|2) as a super-row.
    This flag prevents aggregating, and only marks a row as a suspected spanning cell.
    This retains column information, and lets the user combine spanning rows if so desired.
    """
    
    


    

class TATRFormattedTable(FormattedTable):
    """
    FormattedTable, as seen by a Table Transformer (TATR).
    See :class:`~gmft.TATRTableFormatter`.
    """
    
    _POSSIBLE_ROWS = ['table row', 'table spanning cell', 'table projected row header'] # , 'table column header']
    _POSSIBLE_PROJECTING_ROWS = ['table projected row header'] # , 'table spanning cell']
    _POSSIBLE_COLUMN_HEADERS = ['table column header']
    _POSSIBLE_COLUMNS = ['table column'] 
    id2label = {
        0: 'table',
        1: 'table column',
        2: 'table row',
        3: 'table column header',
        4: 'table projected row header',
        5: 'table spanning cell',
        6: 'no object',
    }
    label2id = {v: k for k, v in id2label.items()}
    
    
    config: TATRFormatConfig
    outliers: dict[str, bool]
    
    effective_rows: list[tuple]
    "Rows as seen by the image --> df algorithm, which may differ from what the table transformer sees."
    
    effective_columns: list[tuple]
    "Columns as seen by the image --> df algorithm, which may differ from what the table transformer sees."
    
    def __init__(self, cropped_table: CroppedTable, fctn_results: dict, 
                #  fctn_scale_factor: float, fctn_padding: tuple[int, int, int, int], 
                 config: TATRFormatConfig=None):
        super(TATRFormattedTable, self).__init__(cropped_table)
        self.fctn_results = fctn_results
        # self.fctn_scale_factor = fctn_scale_factor
        # self.fctn_padding = tuple(fctn_padding)
        
        if config is None:
            config = TATRFormatConfig()
        self.config = config
        self.outliers = None
    def df(self, config_overrides: TATRFormatConfig=None):
        """
        Return the table as a pandas dataframe. 
        :param config_overrides: override the config settings for this call only
        """
        if self._df is not None: # cache
            return self._df
        
        if config_overrides is not None:
            config = copy.deepcopy(self.config)
            config.__dict__.update(config_overrides.__dict__)
        else:
            config = self.config
        
        self._df = extract_to_df(self, config=config)
        return self._df
    
    
    def visualize(self, filter=None, dpi=None, effective=False, **kwargs):
        """
        Visualize the table.
        
        :param filter: filter the labels to visualize. See TATRFormattedTable.id2label
        :param dpi: Sets the dpi. If none, then the dpi of the cached image is used.
        :param effective: if True, visualize the effective rows and columns, which may differ from the table transformer's output.
        """
        if dpi is None: # dpi = needed_dpi
            dpi = self._img_dpi
        if dpi is None:
            dpi = 72
        if self._df is None:
            self._df = self.df()
        scale_by = (dpi / 72)
        
        if effective:
            boxes = [x['bbox'] for x in self.effective_rows + self.effective_columns]
            boxes = [(x * scale_by for x in bbox) for bbox in boxes]
            _to_visualize = {
                "scores": [x['confidence'] for x in self.effective_rows + self.effective_columns],
                "labels": [self.label2id[x['label']] for x in self.effective_rows + self.effective_columns],
                "boxes": boxes
            }
        else:
            # transform functionalized coordinates into image coordinates
            # sf = self.fctn_scale_factor
            # pdg = self.fctn_padding
            # boxes = [_normalize_bbox(bbox, used_scale_factor=sf / scale_by, used_padding=pdg) for bbox in self.fctn_results["boxes"]]
            boxes = [(x * scale_by for x in bbox) for bbox in self.fctn_results["boxes"]]

            _to_visualize = {
                "scores": self.fctn_results["scores"],
                "labels": self.fctn_results["labels"],
                "boxes": boxes
            }
            
        # get needed scale factor and dpi
        img = self.image(dpi=dpi)
        # if self._img is not None:
        plot_results_unwr(img, _to_visualize['scores'], _to_visualize['labels'], _to_visualize['boxes'], TATRFormattedTable.id2label, filter=filter, **kwargs)
            
    def to_dict(self):
        """
        Serialize self into dict
        """
        if self.angle != 0:
            parent = RotatedCroppedTable.to_dict(self)
        else:
            parent = CroppedTable.to_dict(self)
        return {**parent, **{
            # 'fctn_scale_factor': self.fctn_scale_factor,
            # 'fctn_padding': list(self.fctn_padding),
            'config': self.config.__dict__,
            'outliers': self.outliers,
            'fctn_results': self.fctn_results,
        }}
    
    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize from dict
        """
        cropped_table = CroppedTable.from_dict(d, page)
        config = TATRFormatConfig()
        for k, v in d['config'].items():
            if v is not None and config.__dict__.get(k) != v:
                setattr(config, k, v)
        
        results = d['fctn_results']
        if 'fctn_scale_factor' in d or 'scale_factor' in d or 'fctn_padding' in d or 'padding' in d:
            # deprecated: this is for backwards compatibility
            scale_factor = d.get('fctn_scale_factor', d.get('scale_factor', 1))
            padding = d.get('fctn_padding', d.get('padding', (0, 0)))
            padding = tuple(padding)
            
            # normalize results here
            for i, bbox in enumerate(results["boxes"]):
                results["boxes"][i] = _normalize_bbox(bbox, used_scale_factor=scale_factor, used_padding=padding)
            
            
        table = TATRFormattedTable(cropped_table, results, # scale_factor, tuple(padding), 
                                   config=config)
        table.outliers = d.get('outliers', None)
        return table

class TATRTableFormatter(TableFormatter):
    """
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`~gmft.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    
    def __init__(self, config: TATRFormatConfig=None):
        if config is None:
            config = TATRFormatConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(config.image_processor_path)
        self.structor = TableTransformerForObjectDetection.from_pretrained(config.formatter_path)
        self.config = config
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)
    
    def extract(self, table: CroppedTable, dpi=144, padding='auto') -> FormattedTable:
        """
        Extract the data from the table.
        """
        image = table.image(dpi=dpi, padding=padding) # (20, 20, 20, 20)
        padding = table._img_padding
        
        scale_factor = dpi / 72
        encoding = self.image_processor(image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.structor(**encoding)
        
        target_sizes = [image.size[::-1]]
        # threshold = 0.3
        # note that a LOW threshold is good because the model is overzealous in
        # but since we find the highest-intersecting row, same-row elements still tend to stay together
        # this is better than having a high threshold, because if we have fewer rows than expected, we merge cells
        # losing information
        results = self.image_processor.post_process_object_detection(outputs, threshold=self.config.formatter_base_threshold, target_sizes=target_sizes)[0]
        
        

        # create a new FormattedTable instance with the cropped table and the dataframe
        # formatted_table = FormattedTable(table, df)
        
        # return formatted_table
        results = {k: v.tolist() for k, v in results.items()}
        
        # normalize results w.r.t. padding and scale factor
        for i, bbox in enumerate(results["boxes"]):
            results["boxes"][i] = _normalize_bbox(bbox, used_scale_factor=scale_factor, used_padding=padding)
        
        
        formatted_table = TATRFormattedTable(table, results, # scale_factor, padding, 
                                             config=self.config)
        return formatted_table
            

class AutoTableFormatter(TATRTableFormatter):
    """
    The recommended :class:`TableFormatter`. Currently points to :class:`~gmft.TATRTableFormatter`.
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`~gmft.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    pass

class AutoFormatConfig(TATRFormatConfig):
    """
    Configuration for the recommended :class:`TableFormatter`. Currently points to :class:`~gmft.TATRFormatConfig`.
    """
    pass
    

def _priority_row(lbl: dict):
    """
    To deal with overlap, we need to prioritize cells.
    "table column header" is most valuable. 
    "table row" is next value.
    "table spanning cell" is least valuable, and often it overlaps valid rows.
    """
    if lbl == 'table column header':
        return 2
    elif lbl == 'table row':
        return 1
    elif lbl == 'table spanning cell':
        return 0
    return 1
    

def _guess_row_bboxes_for_large_tables(table: TATRFormattedTable, sorted_rows, sorted_headers, known_means=None, known_height=None):
    if known_height:
        row_height = known_height
    else:
        # get the distribution of word heights, rounded to the nearest tenth
        print("Invoking large table row guess! set TATRFormatConfig.large_table_threshold to 999 to disable this.")
        word_heights = []
        for xmin, ymin, xmax, ymax, text in table.text_positions(remove_table_offset=True):
            word_heights.append(round(ymax - ymin, 1))
        # get the mode
        from collections import Counter
        word_heights = Counter(word_heights)
        
        if not sorted_rows:
            return []
        
        # set the mode to be the row height
        # making the row less than text's height will mean that no cells are merged
        # but subscripts may be difficult
        row_height = 0.95 * max(word_heights, key=word_heights.get)
    
    # construct bbox for each row
    leftmost = min([x['bbox'][0] for x in sorted_rows])
    rightmost = max([x['bbox'][2] for x in sorted_rows])
    
    table_ymax = sorted_rows[-1]['bbox'][3]
    # we need to find the number of rows that can fit in the table
    
    # start at the end of the col header
    if sorted_headers:
        y = sorted_headers[-1]['bbox'][3]
    else:
        y = sorted_rows[0]['bbox'][1]
    
    new_rows = []
    if known_means:
        # print(known_means)
        # construct rows, trying to center the rows on the known means
        starting_y = y
        prev_height = None
        for i, mean in enumerate(known_means):
            if mean < starting_y:
                # do not observe the header
                continue
            y = mean - row_height / 2
            # do NOT construct mini row if there is a gap
            # if prev_height is not None and y < prev_height:
                # new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, prev_height, rightmost, y]})
            new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, y, rightmost, y + row_height]})
            prev_height = y + row_height
            
    else:
        # this is reminiscent of the proof that the rationals are dense in the reals
        while y < table_ymax:
            new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [leftmost, y, rightmost, y + row_height]})
            y += row_height
    # 2a. sort by ymax, just in case
    new_rows.sort(key=lambda x: x['bbox'][3])
    return new_rows, row_height
    # return col_headers 
    
    
        

def _normalize_bbox(bbox: tuple[float, float, float, float], used_scale_factor: float, used_padding: tuple[float, float]):
    """
    Normalize bbox such that:
    1. padding is removed (so (0, 0) is the top-left of the cropped table)
    2. scale factor is normalized (dpi=72)
    """
    bbox = [bbox[0] - used_padding[0], bbox[1] - used_padding[1], bbox[2] - used_padding[0], bbox[3] - used_padding[1]]
    bbox = [bbox[0] / used_scale_factor, bbox[1] / used_scale_factor, bbox[2] / used_scale_factor, bbox[3] / used_scale_factor]
    return bbox


def _fill_using_partitions(text_positions: Generator[tuple[float, float, float, float, str], None, None], 
                          config: TATRFormatConfig, 
                          sorted_rows: list[dict], sorted_columns: list[dict], 
                          sorted_headers: list[dict], column_headers: dict[int, list[str]], 
                          row_headers: dict[int, list[str]], outliers: dict[str, bool], 
                        #   large_table_guess: bool, 
                          row_means: list[list[float]]):
    """
    Given estimated positions of rows, columns, headers and text positions,
    fills the table array.
    """

    num_rows = len(sorted_rows)
    num_columns = len(sorted_columns)
    table_array = np.empty([num_rows, num_columns], dtype="object")

    for xmin, ymin, xmax, ymax, text in text_positions:
        
        textbox = (xmin, ymin, xmax, ymax)

        # 5. let row_num be row with max iob
        row_num = None
        row_max_iob = 0
        
        # with binary search, we can only look at filtered subsets
        # get the first row that may intersect the textbox, even a little bit
        # so the first such row_ymax > ymin
        i = _find_leftmost_gt(sorted_rows, ymin, lambda row: row['bbox'][3])
        while i < len(sorted_rows):
            row = sorted_rows[i]
            iob_score = _iob(textbox, row['bbox'])
            if iob_score > row_max_iob:
                row_max_iob = iob_score
                row_num = i
            # we may break early when the row is below the textbox
            # this assumes that row_min and row_max are roughly 
            if ymax < row['bbox'][1]: # ymax < row_min
                break
            i += 1
        
        # 6. look for high iob headers too
        header_max_iob = 0
        for i, header in enumerate(sorted_headers):
            iob_score = _iob(textbox, header['bbox'])
            if iob_score > header_max_iob:
                header_max_iob = iob_score
        
        # only consider 
        # if it could be both header or row, prefer header
        possible_header = header_max_iob >= row_max_iob
        if possible_header and header_max_iob <= 0.5:
            # best cell is a partial overlap; ambiguous
            outliers['skipped col header'] = True
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
            
        if row_num is None and not possible_header:
            # if we ever do not record a value, something awry happened
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
        
        # 6. let column_num be column with max iob
        column_num = None
        column_max_iob = 0
        # find the first column where column_max > xmin
        i = _find_leftmost_gt(sorted_columns, xmin, lambda column: column['bbox'][2])
        while i < len(sorted_columns):
            column = sorted_columns[i]
            iob_score = _iob(textbox, column['bbox'])
            if iob_score > column_max_iob:
                column_max_iob = iob_score
                column_num = i
            if xmax < column['bbox'][0]: # xmax < column_min
                break
            i += 1
        
        # 7. check if it's a header
        if possible_header:
            column_headers.setdefault(column_num, []).append(text)
            continue
        
        # we may now obtain row and column
        # if row_num is None:
            # continue
        row = sorted_rows[row_num]
        if column_num is None:
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
        column = sorted_columns[column_num]
        
        
        # 8. get the putative cell. check if it's a special cell
        if config.aggregate_spanning_cells and row['label'] in ['table projected row header', 'table spanning cell']:
            row_headers.setdefault(row_num, []).append(text)
            continue
        
        # otherwise, we have a regular cell
        cell = Rect(row['bbox']).intersect(column['bbox'])
        
        # get iob: how much of the text is in the cell
        score = _iob(textbox, cell)
        
        if score < config.iob_reject_threshold: # poor match, like if score < 0.2
            outliers['skipped text'] = outliers.get('skipped text', '') + ' ' + text
            continue
        
        # the "non-corner assumption" is that if the textbox has been clipped, it was clipped by
        # an edge and not a corner. For instance, demo|nstration is a clipped text, 
        # but "̵d̵e̵m̵'onstration" ("dem" is clipped by a corner) is invalid.
        
        # We may assume this because the row/column should stretch to the ends of the table
        # we can easily check this by seeing if row_max_iob and col_max_iob are independent
        
        # If this is not true, then it is not true in general that the best cell (most overlap)
        # is given by the intersection of the best row and the best column.
        
        score_norm_deviation = abs(row_max_iob * column_max_iob - score) / score
        if score_norm_deviation > config.corner_clip_outlier_threshold:
            outliers['corner clip'] = True
        
        if score < config.iob_warn_threshold: # If <0.5 is the best, warn but proceed.
            outliers['lowest iob'] = min(outliers.get('lowest iob', 1), score)
        
        # update the table array, and join with ' ' if exists
        if row_means is not None:
            row_median = (ymax + ymin) / 2
            row_means[row_num].append(row_median)
            
        
        if table_array[row_num, column_num] is not None:
            table_array[row_num, column_num] += ' ' + text
        else:
            table_array[row_num, column_num] = text
    
    return table_array

def extract_to_df(table: TATRFormattedTable, config: TATRFormatConfig=None):
    """
    Return the table as a pandas dataframe.
    """
    
    # the tatr authors use a similar method in inference.py
    if config is None:
        config = table.config
    
    outliers = {} # store table-wide information about outliers or pecularities
    
    results = table.fctn_results
    # scale_factor = table.fctn_scale_factor
    # padding = table.fctn_padding

    # 1. collate identified boxes
    boxes = []
    for a, b, c in zip(results["scores"], results["labels"], results["boxes"]):
        bbox = c # .tolist()
        # bbox = _normalize_bbox(bbox, used_scale_factor=scale_factor, used_padding=padding)
        if a >= table.config.cell_required_confidence[b]:
            boxes.append({'confidence': a, 'label': table.id2label[b], 'bbox': bbox})
    
    # for cl, lbl_id, (xmin, ymin, xmax, ymax) in boxes:
    
    sorted_horizontals = []
    sorted_columns = []
    for box in boxes:
        label = box['label']
        if label == 'table spanning cell':
            span_width = box['bbox'][2] - box['bbox'][0]
            if span_width < table.config.spanning_cell_minimum_width * table.rect.width:
                outliers['narrow spanning cell'] = outliers.get('narrow spanning cell', 0) + 1
                continue
        elif label in TATRFormattedTable._POSSIBLE_COLUMN_HEADERS or label in TATRFormattedTable._POSSIBLE_ROWS:
            sorted_horizontals.append(box)
        elif label in TATRFormattedTable._POSSIBLE_COLUMNS:
            sorted_columns.append(box)
    # 2a. sort by ymax
    sorted_horizontals.sort(key=lambda x: x['bbox'][3])
    # 2b. sort by xmax
    sorted_columns.sort(key=lambda x: x['bbox'][2])
    
    # print(len(sorted_rows), len(sorted_columns))
    if not sorted_horizontals or not sorted_columns:
        raise ValueError("No rows or columns detected")

    
    # 3. deduplicate, because tatr places a 2 bboxes for header (it counts as a header and a row)
    # only check consecutive rows/columns
    i = 1
    prev = sorted_horizontals[0]
    while i < len(sorted_horizontals):
        cur = sorted_horizontals[i]
        if _symmetric_iob(prev['bbox'], cur['bbox']) > table.config.deduplication_iob_threshold:
            # pop the one that is a row
            # print("popping something")
            cur_priority = _priority_row(cur['label'])
            prev_priority = _priority_row(prev['label'])
            if cur_priority <= prev_priority:
                # pop cur
                sorted_horizontals.pop(i)
            elif cur_priority > prev_priority:
                sorted_horizontals.pop(i-1)
                prev = cur
        else:
            prev = cur
            i += 1
    
    sorted_rows = []
    sorted_headers = []
    for x in sorted_horizontals:
        if x['label'] in TATRFormattedTable._POSSIBLE_ROWS:
            sorted_rows.append(x)
        else:
            sorted_headers.append(x)
    
    # 4a. calculate total row overlap. If higher than a threshold, invoke the large table assumption
    # also count headers
    table_area = table.rect.width * table.rect.height # * scale_factor ** 2
    total_row_area = 0
    for row in sorted_rows:
        if row['label'] == 'table row':
            total_row_area += (row['bbox'][2] - row['bbox'][0]) * (row['bbox'][3] - row['bbox'][1])
    for row in sorted_headers:
        if row['label'] == 'table projected row header':
            total_row_area += (row['bbox'][2] - row['bbox'][0]) * (row['bbox'][3] - row['bbox'][1])
    
    # large table guess
    large_table_guess = total_row_area > (1 + table.config.large_table_row_overlap_threshold) * table_area \
            and len(sorted_rows) > table.config.large_table_threshold
    
    if large_table_guess:
        sorted_rows, known_height = _guess_row_bboxes_for_large_tables(table, sorted_rows, sorted_headers)
        left_corner = sorted_rows[0]['bbox']
        right_corner = sorted_rows[-1]['bbox']
        # (ymax - ymin) * (xmax - xmin)
        total_row_area = (right_corner[3] - left_corner[1]) * (right_corner[2] - left_corner[0])
        
        # outline: 
        # 1. allot each of the text into its row, which we can actually calculate using
        # (text-ymean / table_height) * num_rows is the index
        # 2. --> this estimate usually does not merge, but it does _split_
        # 2. for each row, calculate the mean of the y-values
        # 3. purge empty rows
        # 4. get a good estimate of the true row height by getting the (median) difference of means between rows
        # 5. (use a centering method (ie. mean, median, etc.) to get the row height, with robustness to split rows)
        # 6. re-estimate the rows
        bins = [[] for _ in range(len(sorted_rows))]
        top = left_corner[1]
        bottom = right_corner[3]
        for xmin, ymin, xmax, ymax, text in table.text_positions(remove_table_offset=True):
            yavg = (ymin + ymax) / 2
            i = int((yavg - top) / (bottom - top) * len(sorted_rows))
            if 0 <= i < len(bins):
                bins[i].append(yavg)
        known_means = [np.mean(x) for x in bins if len(x)]
        
        differences = [known_means[i+1] - known_means[i] for i in range(len(known_means) - 1)]
        known_height = np.median(differences)
        
        # means are within 0.2 * known_height of each other, consolidate them
        i = 1
        while i < len(known_means):
            prev = known_means[i-1]
            cur = known_means[i]
            if abs(cur - prev) < 0.2 * known_height:
                # merge by averaging
                known_means[i-1] = (prev + cur) / 2
                known_means.pop(i)
                
                # don't allow double merging
            i += 1
        
        sorted_rows, known_height = _guess_row_bboxes_for_large_tables(table, sorted_rows, sorted_headers, 
                                                                      known_means=known_means, known_height=known_height)
        
        # bit of deduplication
        # i = 1
        # prev = sorted_rows[0]
        # while i < len(sorted_rows):
        #     cur = sorted_rows[i]
        #     if symmetric_iob(prev['bbox'], cur['bbox']) > table.config.deduplication_iob_threshold:
        #         sorted_rows.pop(i)
        #     else:
        #         prev = cur
        #         i += 1
        
    
    table.effective_rows = sorted_rows
    table.effective_columns = sorted_columns
    
    # 4b. check for catastrophic overlap
    total_column_area = 0
    for col in sorted_columns:
        if col['label'] == 'table column':
            total_column_area += (col['bbox'][2] - col['bbox'][0]) * (col['bbox'][3] - col['bbox'][1])
    # we must divide by 2, because a cell is counted twice by the row + column
    total_area = (total_row_area + total_column_area) / 2
    
    if total_area > (1 + table.config.total_overlap_reject_threshold) * table_area:
        raise ValueError(f"The identified boxes have significant overlap: {total_area / table_area - 1:.2%} of area is overlapping (Max is {table.config.total_overlap_reject_threshold:.2%})")
    
    elif total_area > (1 + table.config.total_overlap_warn_threshold) * table_area:
        outliers['high overlap'] = (total_area / table_area - 1)
    
        
    column_headers = {}
    row_headers = {}
        
    # in case of large_table_guess, keep track of the means of rows
    row_means = None
    if large_table_guess:
        row_means = [[] for _ in range(len(sorted_rows))]
    
    if large_table_guess:

        pass
    table_array = _fill_using_partitions(table.text_positions(remove_table_offset=True), config=config, 
                                        sorted_rows=sorted_rows, sorted_columns=sorted_columns, 
                                        sorted_headers=sorted_headers, column_headers=column_headers, 
                                        row_headers=row_headers, outliers=outliers, row_means=row_means)
    
    # refinement
    
    num_rows = len(sorted_rows)
    num_columns = len(sorted_columns)
    
    # create a pandas dataframe from the table array
    table._df = pd.DataFrame(data=table_array, columns=[' '.join(column_headers.get(i, '')) for i in range(num_columns)])
    
    # if row_headers exist, add it in to the special "row_headers" column, which we preferably insert to the left
    if not table.config.aggregate_spanning_cells:
        # just mark as spanning/non-spanning
        is_spanning = [row['label'] in TATRFormattedTable._POSSIBLE_PROJECTING_ROWS for row in sorted_rows]
        if any(is_spanning):
            # insert at end
            table._df.insert(num_columns, 'is_projecting_row', is_spanning)
    elif row_headers:
        row_headers_list = [' '.join(row_headers.get(i, '')) for i in range(num_rows)]
        row_headers_list = [x if x else None for x in row_headers_list]
        table._df.insert(0, 'row_headers', row_headers_list)
    
    if table.config.remove_null_rows:
        table._df = table._df.dropna(how='all')
    table.outliers = outliers
    return table._df
        
        
    
    
    
    