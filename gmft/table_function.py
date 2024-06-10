from abc import ABC, abstractmethod
import bisect
from math import ceil

from gmft.pdf_bindings import BasePage
import numpy as np
import torch

from gmft.table_visualization import plot_results_orig
from gmft.table_detection import CroppedTable, TableDetectorConfig

import transformers
from transformers import AutoImageProcessor, TableTransformerForObjectDetection
import pandas as pd

from gmft.common import Rect

def iob(bbox1: tuple[float, float, float, float], bbox2: tuple[float, float, float, float]):
    """
    Compute the intersection area over box area, for bbox1.
    """
    intersection = Rect(bbox1).intersect(bbox2)
    
    bbox1_area = Rect(bbox1).area
    if bbox1_area > 0:
        return intersection.area / bbox1_area
    
    return 0

def symmetric_iob(bbox1, bbox2):
    """
    Compute the intersection area over box area, for min of bbox1 and bbox2
    """
    intersection = Rect(bbox1).intersect(bbox2)
    
    bbox1_area = Rect(bbox1).area
    bbox2_area = Rect(bbox2).area
    if bbox1_area > 0 and bbox2_area > 0:
        return intersection.area / min(bbox1_area, bbox2_area)
    
    return 0

class FormattedTable(CroppedTable):
    """
    This is a table that is *formatted*, which is to say it is "functionalized" with header and data information. 
    Therefore, it can be converted into df, csv, etc.
    """
    
    
    def __init__(self, cropped_table: CroppedTable, df: pd.DataFrame=None):
        self._df = df
        
        # create shallow copy
        self.page = cropped_table.page
        self.rect = cropped_table.rect
        self.bbox = cropped_table.bbox
        self.confidence_score = cropped_table.confidence_score
        self.label = cropped_table.label
        
        self._img = cropped_table._img.copy()
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




class TableFunctionalizer(ABC):
    """
    Abstract class for converting a table of data, and extracting the data from it.
    
    """
    
    @abstractmethod
    def extract(self, table: CroppedTable) -> FormattedTable:
        """
        Extract the data from the table.
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
    
    # ---- model settings ----
    
    warn_uninitialized_weights: bool = False
    image_processor_path: str = "microsoft/table-transformer-detection"
    formatter_path: str = "microsoft/table-transformer-structure-recognition"
    
    # base threshold for the confidence demanded of a table feature (row/column)
    # note that a low threshold is actually better, because overzealous rows means that
    # generally, numbers are still aligned and there are just many empty rows
    # (having fewer rows than expected merges cells, which is bad)
    formatter_base_threshold: float = 0.3
    
    # Confidences required (>=) for a row/column feature to be considered good. See TATRFormattedTable.id2label
    # But see formatter_threshold on why having low confidences may be better than too high confidence
    cell_required_confidence = {
        0: 0.3, 
        1: 0.3, 
        2: 0.3, 
        3: 0.3, 
        4: 0.3, 
        5: 0.3,
        6: 99
    }
    
    # ---- df() settings ----
    
    # with large tables, table transformer struggles with placing too many overlapping rows
    # luckily, with more rows, we have more info on the usual size of text, which we can use to make
    # a guess on the height such that no rows are merged or overlapping
    
    # large table assumption is only applied when (# of rows > 50) AND (total overlap > 20%)
    # set 9999 to disable, set 0 to force large table assumption to run every time
    large_table_threshold = 20
    large_table_total_overlap_threshold = 0.15

    # reject if total overlap is > 20% of table area
    total_overlap_reject_threshold = 0.2
    # warn if total overlap is > 5% of table area
    total_overlap_warn_threshold = 0.05
    # "corner clip" is when the text is clipped by a corner, and not an edge
    corner_clip_outlier_threshold = 0.1
    # reject if iob < 5%
    iob_reject_threshold = 0.05
    # warn if iob < 50%
    iob_warn_threshold = 0.5
    # remove rows with no data
    remove_null_rows = True 
    
    spanning_cell_minimum_width = 0.6 # having trouble with row headers falsely detected as spanning cells
    # so this prunes certain cells
    # set 0 to keep all spanning cells
    
    # iob threshold for deduplication
    # if 2 consecutive rows have iob > 0.95, then one of them gets deleted (!)
    deduplication_iob_threshold = 0.95
    
    # TATR seems to have a high spanning cell false positive rate. 
    # (spanning cell or projected row header)
    # That is, it identifies a regular row with information (ie. Retired|5|3|2) as a super-row.
    # This flag prevents aggregating, and only marks a row as a suspected spanning cell.
    # This retains column information, and lets the user combine spanning rows if so desired.
    aggregate_spanning_cells = False
    
    


    

class TATRFormattedTable(FormattedTable):
    """
    """
    
    _POSSIBLE_ROWS = ['table row', 'table spanning cell', 'table projected row header'] # , 'table column header']
    _POSSIBLE_SPANNING_ROWS = ['table projected row header', 'table spanning cell']
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
    def __init__(self, cropped_table: CroppedTable, fctn_results: dict, scale_factor: float, padding: tuple[int, int], config: TATRFormatConfig=None):
        super(TATRFormattedTable, self).__init__(cropped_table)
        self.fctn_results = fctn_results
        self.scale_factor = scale_factor
        self.padding = padding
        
        if config is None:
            config = TATRFormatConfig()
        self.config = config
        self.outliers = None
    def df(self):
        """
        Return the table as a pandas dataframe.
        """
        if self._df is not None: # cache
            return self._df
        
        self._df = extract_to_df(self)
        return self._df
    
    
    def visualize(self, filter=None):
        """
        Visualize the table.
        """
        if self._img is not None:
            plot_results_orig(self._img, self.fctn_results, TATRFormattedTable.id2label, filter=filter)
        else:
            raise ValueError("No image available to visualize")
    
    def to_dict(self):
        """
        Serialize self into dict
        """
        parent = CroppedTable.to_dict(self)
        return {**parent, **{
            'scale_factor': self.scale_factor,
            'padding': self.padding,
            'config': self.config.__dict__,
            'outliers': self.outliers,
            'fctn_results': {k: v.tolist() for k, v in self.fctn_results.items()},
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
        return TATRFormattedTable(cropped_table, d['fctn_results'], d['scale_factor'], tuple(d['padding']), config=config)

class TATRTableFormatter(TableFunctionalizer):
    
    

    
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
        
        formatted_table = TATRFormattedTable(table, results, scale_factor, padding, config=self.config)
        return formatted_table
            
            
def priority_row(lbl: dict):
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
    

def guess_row_bboxes_for_large_tables(table: TATRFormattedTable, sorted_rows, sorted_headers):
    # get the distribution of word heights, rounded to the nearest tenth
    print("Invoking large table row guess! set TATRFormatConfig.large_table_threshold to 999 to disable this.")
    word_heights = []
    for xmin, ymin, xmax, ymax, text in table.text_positions(remove_table_offset=True):
        word_heights.append(round(ymax - ymin, 1))
    # get the mode
    from collections import Counter
    word_heights = Counter(word_heights)
    
    # set the mode to be the row height
    # making the row less than text's height will mean that no cells are merged
    # but subscripts may be difficult
    row_height = 0.95 * max(word_heights, key=word_heights.get)
    
    # construct bbox for each row
    prev_row_xmin = min([x['bbox'][0] for x in sorted_rows])
    prev_row_xmax = max([x['bbox'][2] for x in sorted_rows])
    
    table_ymax = sorted_rows[-1]['bbox'][3]
    # we need to find the number of rows that can fit in the table
    
    # of the rows, retain column headers only
    # col_headers = [x for x in sorted_rows if x['label'] == 'table column header']
    # start at the end of the col header
    y = sorted_headers[-1]['bbox'][3]
    
    new_rows = []
    while y < table_ymax:
        new_rows.append({'confidence': 1, 'label': 'table row', 'bbox': [prev_row_xmin, y, prev_row_xmax, y + row_height]})
        y += row_height
    # 2a. sort by ymax, just in case
    new_rows.sort(key=lambda x: x['bbox'][3])
    return new_rows
    # return col_headers 
    
    
        
            
def extract_to_df(table: TATRFormattedTable):
    """
    Return the table as a pandas dataframe.
    """

    # the tatr authors use a similar method in inference.py
    
    outliers = {} # store table-wide information about outliers or pecularities
    
    results = table.fctn_results
    scale_factor = table.scale_factor
    padding = table.padding

    # 1. collate identified boxes
    boxes = []
    for a, b, c in zip(results["scores"], results["labels"], results["boxes"]):
        bbox = c.tolist()
        bbox = [bbox[0] - padding[0], bbox[1] - padding[1], bbox[2] - padding[0], bbox[3] - padding[1]]
        bbox = [bbox[0] / scale_factor, bbox[1] / scale_factor, bbox[2] / scale_factor, bbox[3] / scale_factor]
        if a.item() >= table.config.cell_required_confidence[b.item()]:
            boxes.append({'confidence': a.item(), 'label': table.id2label[b.item()], 'bbox': bbox})
    
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
        if symmetric_iob(prev['bbox'], cur['bbox']) > table.config.deduplication_iob_threshold:
            # pop the one that is a row
            # print("popping something")
            cur_priority = priority_row(cur['label'])
            prev_priority = priority_row(prev['label'])
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
    
    

    # 4. check for catastrophic overlap
    table_area = table.rect.width * table.rect.height # * scale_factor ** 2
    total_area = 0
    for row in sorted_rows:
        if row['label'] == 'table row':
            total_area += (row['bbox'][2] - row['bbox'][0]) * (row['bbox'][3] - row['bbox'][1])
    for row in sorted_headers:
        if row['label'] == 'table row':
            total_area += (row['bbox'][2] - row['bbox'][0]) * (row['bbox'][3] - row['bbox'][1])
    for col in sorted_columns:
        if col['label'] == 'table column':
            total_area += (col['bbox'][2] - col['bbox'][0]) * (col['bbox'][3] - col['bbox'][1])
    # we must divide by 2, because a cell is counted twice by the row + column
    total_area /= 2
    
    if total_area > (1 + table.config.large_table_total_overlap_threshold) * table_area \
            and len(sorted_rows) > table.config.large_table_threshold:
        sorted_rows = guess_row_bboxes_for_large_tables(table, sorted_rows, sorted_headers)
    
    elif total_area > (1 + table.config.total_overlap_reject_threshold) * table_area:
        raise ValueError(f"The identified boxes have significant overlap: {total_area / table_area - 1:.2%} of area is overlapping (Max is {table.config.total_overlap_reject_threshold:.2%})")
    
    elif total_area > (1 + table.config.total_overlap_warn_threshold) * table_area:
        outliers['high overlap'] = (total_area / table_area - 1)
    
    num_rows = len(sorted_rows)
    num_columns = len(sorted_columns)
    
    # print(num_rows, num_columns)
    
    table_array = np.empty([num_rows, num_columns], dtype="object")
    
    column_headers = {}
    row_headers = {}
        
    
    for xmin, ymin, xmax, ymax, text in table.text_positions(remove_table_offset=True):
        
        # TODO see if there's a way to find max_header with binary search
        # O(n (w + h)) ~ O(n sqrt(n)) is linear search
        # O(n (logw + logh)) ~ O(n (2log(sqrtn)) = O(nlogn) is binary search, but we 
        
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
            iob_score = iob(textbox, row['bbox'])
            if iob_score > row_max_iob:
                row_max_iob = iob_score
                row_num = i
            # we may break early when the row is below the textbox
            # this assumes that row_min and row_max are roughly 
            if ymax < row['bbox'][1]: # ymax < row_min
                break
            i += 1
        # for i, row in enumerate(sorted_rows):
        #     iob_score = iob(textbox, row['bbox'])
        #     if iob_score > row_max_iob:
        #         row_max_iob = iob_score
        #         row_num = i
        #     if xmax < row['bbox'][0]: # xmax < row_min
        #         break
        
        # 6. look for high iob headers too
        header_max_iob = 0
        for i, header in enumerate(sorted_headers):
            iob_score = iob(textbox, header['bbox'])
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
            iob_score = iob(textbox, column['bbox'])
            if iob_score > column_max_iob:
                column_max_iob = iob_score
                column_num = i
            if xmax < column['bbox'][0]: # xmax < column_min
                break
            i += 1
        # for i, column in enumerate(sorted_columns):
        #     iob_score = iob(textbox, column['bbox'])
        #     if iob_score > column_max_iob:
        #         column_max_iob = iob_score
        #         column_num = i
        #     if xmax < column['bbox'][0]: # xmax < column_min
        #         break
        
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
        if table.config.aggregate_spanning_cells and row['label'] in ['table projected row header', 'table spanning cell']:
            row_headers.setdefault(row_num, []).append(text)
            continue
        
        # otherwise, we have a regular cell
        cell = Rect(row['bbox']).intersect(column['bbox'])
        
        # get iob: how much of the text is in the cell
        score = iob(textbox, cell)
        
        if score < table.config.iob_reject_threshold: # poor match, like if score < 0.2
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
        if score_norm_deviation > table.config.corner_clip_outlier_threshold:
            outliers['corner clip'] = True
        
        if score < table.config.iob_warn_threshold: # If <0.5 is the best, warn but proceed.
            outliers['lowest iob'] = min(outliers.get('lowest iob', 1), score)
        
        # update the table array, and join with ' ' if exists
        if table_array[row_num, column_num] is not None:
            table_array[row_num, column_num] += ' ' + text
        else:
            table_array[row_num, column_num] = text
        
    
    # create a pandas dataframe from the table array
    table._df = pd.DataFrame(data=table_array, columns=[' '.join(column_headers.get(i, '')) for i in range(num_columns)])
    
    # if row_headers exist, add it in to the special "row_headers" column, which we preferably insert to the left
    if not table.config.aggregate_spanning_cells:
        # just mark as spanning/non-spanning
        is_spanning = [row['label'] in TATRFormattedTable._POSSIBLE_SPANNING_ROWS for row in sorted_rows]
        if any(is_spanning):
            # insert at end
            table._df.insert(num_columns, 'is_spanning_row', is_spanning)
    elif row_headers:
        row_headers_list = [' '.join(row_headers.get(i, '')) for i in range(num_rows)]
        row_headers_list = [x if x else None for x in row_headers_list]
        table._df.insert(0, 'row_headers', row_headers_list)
    
    if table.config.remove_null_rows:
        table._df = table._df.dropna(how='all')
    table.outliers = outliers
    return table._df
        
        
    
    
    
    