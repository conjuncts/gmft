
import copy
from dataclasses import dataclass, field
import statistics
from typing import Generator, Union

import numpy as np
import pandas as pd

from gmft._dataclasses import removed_property, non_defaults_only, with_config
from gmft.algo.dividers import fill_using_true_partitions, _find_all_intervals_for_interval, _ioa, get_good_between_dividers
from gmft.detectors.common import CroppedTable, RotatedCroppedTable
from gmft.formatters.common import FormattedTable, TableFormatter, _normalize_bbox
from gmft.formatters.histogram import HistogramConfig, HistogramFormattedTable
from gmft.pdf_bindings.common import BasePage


from gmft.table_function_algorithm import _iob, _is_within_header, _non_maxima_suppression, _semantic_spanning_fill, _split_spanning_cells, extract_to_df
from gmft.table_visualization import plot_results_unwr, plot_shaded_boxes

import torch
from transformers import DetrForObjectDetection

@dataclass
class DITRFormatConfig(HistogramConfig):
    """
    Configuration for :class:`.DITRTableFormatter`.
    """
    
    # ---- model settings ----
    
    warn_uninitialized_weights: bool = False
    image_processor_path: str = "microsoft/table-transformer-structure-recognition-v1.1-all"
    formatter_path: str = "conjuncts/ditr-e15"
    # no_timm: bool = True # use a model which uses AutoBackbone. 
    torch_device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    verbosity: int = 1
    """
    0: errors only\n
    1: print warnings\n
    2: print warnings and info\n
    3: print warnings, info, and debug
    """

    formatter_base_threshold: float = 0.3
    """Base threshold for the confidence demanded of a separating line.
    
    Since merged rows are generally harder to deal with than empty rows, a low threshold is usually
    better, because then more separating lines are detected.
    """
    
    cell_required_confidence: dict = field(default_factory=lambda: {
        0: 0.3, # table
        1: 0.3, # column
        2: 0.3, # row
        3: 0.3, # column header
        4: 0.5, # projected row header
        5: 0.5, # spanning cell
        6: 99   # no object
    })
    """Confidences required (>=) for a row/column feature to be considered good. See DITRFormattedTable.id2label
    
    But low confidences may be better than too high confidence (see formatter_base_threshold)
    """
    
    # ---- df() settings ----
    
    # ---- options ----
    
    remove_null_rows: bool = True 
    """Remove rows with no text."""
    
    enable_multi_header: bool = True
    """Enable multi-indices in the dataframe.
    If false, then multiple headers will be merged column-wise."""
    
    semantic_spanning_cells: bool = True
    """
    [Experimental] Enable semantic spanning cells, which often encode hierarchical multi-level indices.
    """
    
    semantic_hierarchical_left_fill: Union[str, None] = 'deep'
    """
    [Experimental] When semantic spanning cells is enabled, when a left header is detected which might
    represent a group of rows, that same value is reduplicated for each row.
    Possible values: 'algorithm', 'deep', None.
    
    'algorithm': assumes that the higher-level header is always the first row followed by several empty rows.\n
    'deep': merges headers according to the spanning cells detected by the Table Transformer.\n
    None: headers are not duplicated.
    """
    
    # ---- large table ----
    
    # note that the overlap metric is not useful anymore since separating lines are not 
    # supposed to cover the entire table.
    
    # hence nms is also not useful anymore.
    
    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def large_table_if_n_rows_removed(self):
        pass

    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def large_table_threshold(self):
        pass
    
    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def large_table_row_overlap_threshold(self):
        pass
    
    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def force_large_table_assumption(self):
        pass
    
    large_table_maximum_rows: int = 1000
    """If the table predicts a large number of rows, refuse to proceed. Therefore prevent memory issues for super small text."""

    # ---- rejection and warnings ----

    # note that the overlap metric is not useful anymore since separating lines are not 
    # supposed to cover the entire table.
    
    # hence nms is also not useful anymore.
    
    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def total_overlap_reject_threshold(self):
        pass
    
    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def total_overlap_warn_threshold(self):
        pass
    
    @removed_property("Overlap (nms) ({name}) is not used for the DITR model.")
    def nms_warn_threshold(self):
        pass
    
    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def iob_reject_threshold(self):
        pass
    
    @removed_property("Overlap ({name}) is not used for the DITR model.")
    def iob_warn_threshold(self):
        pass
    
    # ---- technical ----
    
    _nms_overlap_threshold: float = 0.1
    _nms_overlap_threshold_larger: float = 0.5
    
    @removed_property("Large table approach ({name}) is not used for the DITR model.")
    def _large_table_merge_distance(self):
        pass
    
    _smallest_supported_text_height: float = 0.1
    """The smallest supported text height. Text smaller than this height will be ignored. 
    Helps prevent very small text from creating huge arrays under large table assumption."""
    
    # ---- deprecated ----
    # aggregate_spanning_cells = False
    @removed_property
    def aggregate_spanning_cells(self):
        pass
    # corner_clip_outlier_threshold = 0.1
    # """"corner clip" is when the text is clipped by a corner, and not an edge"""
    @removed_property
    def corner_clip_outlier_threshold(self):
        pass
    
    # spanning_cell_minimum_width = 0.6
    @removed_property
    def spanning_cell_minimum_width(self):
        pass
    
    @property
    def deduplication_iob_threshold(self):
        pass


class DITRFormattedTable(HistogramFormattedTable):
    """
    FormattedTable, as seen by a Table Transformer for dividers (dubbed DITR).
    See :class:`.DITRTableFormatter`.
    """
    
    id2label = {
        # 0: 'table',
        1: 'column divider', # table column',
        2: 'row divider', # table row',
        3: 'top header', # table column header',
        4: 'projected', # 'table projected row header',
        0: 'spanning', # 'table spanning cell',
        6: 'no object',
    }
    label2id = {v: k for k, v in id2label.items()}
    
    config: DITRFormatConfig
    outliers: dict[str, bool]
    
    effective_headers: list[tuple]
    "Headers as seen by the image --> df algorithm."
    
    effective_projecting: list[tuple]
    "Projected rows as seen by the image --> df algorithm."
    
    effective_spanning: list[tuple]
    "Spanning cells as seen by the image --> df algorithm."
    
    _top_header_indices: list[int]=None
    _projecting_indices: list[int]=None
    _hier_left_indices: list[int]=None
    
    def __init__(self, cropped_table: CroppedTable, 
                 irvl_results: dict,
                 fctn_results: dict, 
                #  fctn_scale_factor: float, fctn_padding: tuple[int, int, int, int], 
                 config: DITRFormatConfig=None):
        super(DITRFormattedTable, self).__init__(cropped_table, None, irvl_results, config=config)
        self.fctn_results = fctn_results

        if config is None:
            config = DITRFormatConfig()
        self.config = config
        self.outliers = None
    def df(self, recalculate=False, config_overrides: DITRFormatConfig=None):
        """
        Return the table as a pandas dataframe. 
        :param recalculate: by default, the dataframe is cached
        :param config_overrides: override the config settings for this call only
        """
        if recalculate != False:
            raise DeprecationWarning("recalculate as a parameter in df() is deprecated; explicitly call recompute() instead.")
        
        if self._df is None:
            self.recompute(config=config_overrides)
        return self._df
    
    def recompute(self, config: DITRFormatConfig=None):
        """
        Recompute the internal dataframe.
        """
        config = with_config(self.config, config)
        self._df = ditr_extract_to_df(self, config=config)
        return self._df
    
    def visualize(self, **kwargs):
        """
        Visualize the cropped table.
        """
        img = self.image()
        # labels = self.fctn_results['labels']
        # bboxes = self.fctn_results['boxes']
        tbl_width = self.width # adjust for rotations too
        tbl_height = self.height
        
        labels = []
        bboxes = []
        for x0, x1 in self.irvl_results['col_dividers']:
            bboxes.append([x0, 0, x1, tbl_height])
            labels.append(1)
        for y0, y1 in self.irvl_results['row_dividers']:
            bboxes.append([0, y0, tbl_width, y1])
            labels.append(2)
        for x0, y0, x1, y1 in self.effective_headers:
            bboxes.append([x0, y0, x1, y1])
            labels.append(3)
        for x0, y0, x1, y1 in self.effective_projecting:
            bboxes.append([x0, y0, x1, y1])
            labels.append(4)
        for x0, y0, x1, y1 in self.effective_spanning:
            bboxes.append([x0, y0, x1, y1])
            labels.append(5)
        return plot_shaded_boxes(img, labels=labels, boxes=bboxes, **kwargs)
            
    def to_dict(self):
        """
        Serialize self into dict
        """
        if self.angle != 0:
            parent = RotatedCroppedTable.to_dict(self)
        else:
            parent = CroppedTable.to_dict(self)
        optional = {}
        if self._projecting_indices is not None:
            optional['_projecting_indices'] = self._projecting_indices
        if self._hier_left_indices is not None:
            optional['_hier_left_indices'] = self._hier_left_indices
        if self._top_header_indices is not None:
            optional['_top_header_indices'] = self._top_header_indices
        return {**parent, **{
            # 'fctn_scale_factor': self.fctn_scale_factor,
            # 'fctn_padding': list(self.fctn_padding),
            'config': non_defaults_only(self.config),
            'outliers': self.outliers,
            'fctn_results': self.fctn_results,
        }, **optional}
    
    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize from dict.
        A page is required partly because of memory management, since having this open a page may cause memory issues.
        """
        d = copy.deepcopy(d) # don't modify the original dict
        cropped_table = CroppedTable.from_dict(d, page)
        
        if 'fctn_results' not in d:
            raise ValueError("fctn_results not found in dict -- dict may be a CroppedTable but not a TATRFormattedTable.")
        
        config = DITRFormatConfig(**d['config'])
        
        results = d['fctn_results'] # fix shallow copy issue
        if 'fctn_scale_factor' in d or 'scale_factor' in d or 'fctn_padding' in d or 'padding' in d:
            # deprecated: this is for backwards compatibility
            scale_factor = d.get('fctn_scale_factor', d.get('scale_factor', 1))
            padding = d.get('fctn_padding', d.get('padding', (0, 0)))
            padding = tuple(padding)
            
            # normalize results here
            for i, bbox in enumerate(results["boxes"]):
                results["boxes"][i] = _normalize_bbox(bbox, used_scale_factor=scale_factor, used_padding=padding)
            
            
        table = DITRFormattedTable(cropped_table, None, results, # scale_factor, tuple(padding), 
                                   config=config)
        table.recompute()
        table.outliers = d.get('outliers', None)
        return table

class DITRFormatter(TableFormatter):
    """
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.
    
    Using :meth:`extract`, a :class:`.FormattedTable` is produced, which can be exported to csv, df, etc.
    """
    
    def __init__(self, config: DITRFormatConfig=None):
        import transformers
        from transformers import AutoImageProcessor, TableTransformerForObjectDetection
        
        if config is None:
            config = DITRFormatConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(config.image_processor_path)
        # revision = "no_timm" if config.no_timm else None , revision=revision
        self.structor = TableTransformerForObjectDetection.from_pretrained(config.formatter_path).to(config.torch_device)
        self.config = config
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)
    
    def extract(self, table: CroppedTable, dpi=144, padding='auto', margin=None, config_overrides=None) -> DITRFormattedTable:
        """
        Extract the data from the table.
        """
        
        config = with_config(self.config, config_overrides)
        
        image = table.image(dpi=dpi, padding=padding, margin=margin) # (20, 20, 20, 20)
        padding = table._img_padding
        margin = table._img_margin
        
        scale_factor = dpi / 72
        encoding = self.image_processor(image, size={"shortest_edge": 800, "longest_edge": 1333}, return_tensors="pt").to(self.config.torch_device)
        with torch.no_grad():
            outputs = self.structor(**encoding)
        
        target_sizes = [image.size[::-1]]
        results = self.image_processor.post_process_object_detection(outputs, threshold=config.formatter_base_threshold, target_sizes=target_sizes)[0]
        
        # return formatted_table
        results = {k: v.tolist() for k, v in results.items()}
        
        # normalize results w.r.t. padding and scale factor
        for i, bbox in enumerate(results["boxes"]):
            results["boxes"][i] = _normalize_bbox(bbox, used_scale_factor=scale_factor, used_padding=padding, used_margin=margin)
        
        formatted_table = DITRFormattedTable(table, None, results, # scale_factor, padding, 
                                             config=config)
        formatted_table.recompute()
        return formatted_table

class DITRLabel:
    """
    Enum for the labels used by the Table Transformer.
    """
    column_divider = 1
    row_divider = 2
    top_header = 3
    projected = 4
    spanning = 0
    no_object = 6


  

def _determine_headers_and_projecting(row_intervals, sorted_headers, sorted_projecting, iob_threshold=0.7):
    """
    Splits the sorted_horizontals into rows, headers, and projecting rows. 
    Then, identifies a list of indices of headers and projecting rows.
    
    :param row_intervals: list of tuples, each tuple is a row interval (y0, y1)
    :param sorted_headers: list of bboxes (x0, y0, x1, y1) of headers
    :param sorted_projecting: list of bboxes (x0, y0, x1, y1) of projecting rows
    """
    
    # determine which rows overlap (> 0.9) with headers
    header_indices = []
    projecting_indices = []
    
    # iterate through pairs of row dividers
    # consider = [table_bounds[1]] + row_dividers + [table_bounds[3]]
    # for i in range(len(consider) - 1):
        # row_y_interval = (consider[i], consider[i+1])
    for i, row_y_interval in enumerate(row_intervals):
        # probably don't need to binary-ify, because usually the # of headers is 1
        for _, header_y0, _, header_y1 in sorted_headers:
            if _ioa(row_y_interval, (header_y0, header_y1)) > iob_threshold:
                header_indices.append(i)
        else:
            for _, proj_y0, _, proj_y1 in sorted_projecting:
                if _ioa(row_y_interval, (proj_y0, proj_y1)) > iob_threshold:
                    projecting_indices.append(i)
                    break
    return header_indices, projecting_indices

def _non_maxima_suppression_t(sorted_rows: list[tuple], overlap_threshold=0.1):
    """
    accepts (xmin, ymin, xmax, ymax, confidence)
    """
    num_removed = 0
    i = 1
    while i < len(sorted_rows):
        prev = sorted_rows[i-1]
        cur = sorted_rows[i]
        if _iob(prev[:4], cur[:4]) > overlap_threshold:
            if prev[4] > cur[4]:
                sorted_rows.pop(i)
            else:
                sorted_rows.pop(i-1)
            num_removed += 1
        else:
            i += 1
    return num_removed

def proportion_fctn_results(fctn_results: dict, config: DITRFormatConfig) -> \
    tuple[
        list[tuple[float, float, float, float, float]], 
        list[tuple[float, float, float, float, float]], 
        list[tuple[float, float, float, float]], 
        list[tuple[float, float, float, float]], 
        list[dict]
    ]:
    """
    Proportion the fctn_results into 5 categories:
    
    1. column dividers
    2. row dividers
    3. top headers
    4. projected rows
    5. spanning cells
    
    The first 2 are stored as tuples: (xmin, ymin, xmax, ymax, confidence).
    All are stored as direct tuples: (xmin, ymin, xmax, ymax), 
    EXCEPT for the spanning cells, which is stored as a dict with keys 'bbox', 'confidence'.
    """
    # collated = []
    row_divider_boxes = []
    col_divider_boxes = []
    top_headers = []
    projected = []
    spanning_cells = []
    for confidence, label, bbox in zip(fctn_results["scores"], fctn_results["labels"], fctn_results["boxes"]):
        if confidence < config.cell_required_confidence[label]: # remove the unconfident
            continue
        if label == DITRLabel.row_divider:
            row_divider_boxes.append((*bbox, confidence))
        elif label == DITRLabel.column_divider:
            col_divider_boxes.append((*bbox, confidence))
        elif label == DITRLabel.top_header:
            top_headers.append(bbox)
        elif label == DITRLabel.projected:
            projected.append(bbox)
        elif label == DITRLabel.spanning:
            spanning_cells.append({'bbox': bbox, 'confidence': confidence})
    return row_divider_boxes, col_divider_boxes, top_headers, projected, spanning_cells

def empirical_table_bbox(row_divider_boxes, col_divider_boxes):
    """
    We have access to the table bbox from the cropped table, but we can
    also estimate it from the dividers.

    I guess we could also take the max width/height of every divider.
    """
    average_x0 = statistics.mean([box[0] for box in col_divider_boxes]) if col_divider_boxes else -np.inf
    average_x1 = statistics.mean([box[2] for box in col_divider_boxes]) if col_divider_boxes else np.inf
    average_y0 = statistics.mean([box[1] for box in row_divider_boxes]) if row_divider_boxes else -np.inf
    average_y1 = statistics.mean([box[3] for box in row_divider_boxes]) if row_divider_boxes else np.inf
    return (average_x0, average_x1, average_y0, average_y1)

def ditr_fctn_results_to_irvl(fctn_results: dict, table_bounds: tuple[float, float, float, float], config: DITRFormatConfig):
    """
    Convert fctn_results into irvl_results.
    irvl_results = {
        'row_dividers': list of row dividers, of form (y0, y1) (assumed to stretch the width of the table),
        'col_dividers': list of column dividers, of form (x0, x1) (assumed to stretch the height of the table)
    }
    """
    


def ditr_extract_to_df(table: DITRFormattedTable, config: DITRFormatConfig=None):
    """
    Return the table as a pandas dataframe.
    The code is adapted from the TATR authors' inference.py, with a few tweaks.
    """
    
    if config is None:
        config = table.config
    
    outliers = {} # store table-wide information about outliers or pecularities
    
    results = table.fctn_results
    row_divider_boxes, col_divider_boxes, top_headers, projected, spanning_cells = proportion_fctn_results(results, config)

    # Phase I: Separating lines
    
    # 2a. sort by ymean, xmean
    row_divider_boxes.sort(key=lambda box: (box[1] + box[3]) / 2)
    col_divider_boxes.sort(key=lambda box: (box[0] + box[3]) / 2)

    # apply nms
    _non_maxima_suppression_t(row_divider_boxes, overlap_threshold=config._nms_overlap_threshold)
    _non_maxima_suppression_t(col_divider_boxes, overlap_threshold=config._nms_overlap_threshold)
    
    row_dividers = [(y0 + y1) / 2 for x0, y0, x1, y1, _ in row_divider_boxes]
    col_dividers = [(x0 + x1) / 2 for x0, y0, x1, y1, _ in col_divider_boxes]

    row_divider_intervals = [(y0, y1) for _, y0, _, y1, _ in row_divider_boxes]
    col_divider_intervals = [(x0, x1) for x0, _, x1, _, _ in col_divider_boxes]
    table.irvl_results = {
        'row_dividers': row_divider_intervals,
        'col_dividers': col_divider_intervals
    }
    table.effective_headers = top_headers
    table.effective_projecting = projected
    table.effective_spanning = [span['bbox'] for span in spanning_cells]


    # table_bounds = table.bbox # empirical_table_bbox(row_divider_boxes, col_divider_boxes)
    fixed_table_bounds = (0, 0, table.width, table.height) # adjust for rotations too
    

    table_array = fill_using_true_partitions(table.text_positions(remove_table_offset=True), 
                                        row_dividers=row_dividers, column_dividers=col_dividers,
                                        table_bounds=fixed_table_bounds)
        
    # delete empty rows
    if config.remove_null_rows:
        empty_rows = [n for n in range(len(row_dividers)+1) if all(x is None for x in table_array[n, :])]
    else:
        empty_rows = []

    
    num_rows = len(row_dividers) + 1
    num_columns = len(col_dividers) + 1
    
    # Phase II: Rowspan and Colspan.
    
    # note that row intervals are not used to place text, 
    # but rather for functional analysis to determine which rows
    # are headers, projecting, spanning, etc.

    # need to add inverted to make sense of header_indices

    good_row_intervals = get_good_between_dividers(row_divider_intervals, fixed_table_bounds[1], fixed_table_bounds[3], add_inverted=True) 
    good_column_intervals = get_good_between_dividers(col_divider_intervals, fixed_table_bounds[0], fixed_table_bounds[2], add_inverted=True)

    # find indices of key rows
    header_indices, projecting_indices = _determine_headers_and_projecting(good_row_intervals, top_headers, projected)

    if empty_rows:
        header_indices = [i for i in header_indices if i not in empty_rows]
        projecting_indices = [i for i in projecting_indices if i not in empty_rows]

    # semantic spanning fill
    if config.semantic_spanning_cells:

        # TODO probably not worth it to duplicate the code
        old_rows = [(None, y0, None, y1) for y0, y1 in good_row_intervals]
        old_columns = [(x0, None, x1, None) for x0, x1 in good_column_intervals]

        sorted_hier_top_headers, sorted_monosemantic_top_headers, sorted_hier_left_headers = \
            _split_spanning_cells(spanning_cells, top_headers, old_rows, old_columns, header_indices)
        # since these are inherited from spanning cells, NMS is still necessary
        _non_maxima_suppression(sorted_hier_top_headers, overlap_threshold=config._nms_overlap_threshold_larger)
        _non_maxima_suppression(sorted_monosemantic_top_headers, overlap_threshold=config._nms_overlap_threshold_larger)
        _non_maxima_suppression(sorted_hier_left_headers, overlap_threshold=config._nms_overlap_threshold_larger)
        hier_left_idxs = _semantic_spanning_fill(table_array, sorted_hier_top_headers, sorted_monosemantic_top_headers, sorted_hier_left_headers,
                header_indices=header_indices,
                config=config)
        table._hier_left_indices = hier_left_idxs 
    else:
        table._hier_left_indices = [] # for the user
    
    # technically these indices will be off by the number of header rows ;-;
    if config.enable_multi_header:
        table._top_header_indices = header_indices
    else:
        table._top_header_indices = [0] if header_indices else []

    
    # extract out the headers
    header_rows = table_array[header_indices]
    if config.enable_multi_header and len(header_rows) > 1:
        # Convert header rows to a list of tuples, where each tuple represents a column
        columns_tuples = list(zip(*header_rows))

        # Create a MultiIndex with these tuples
        column_headers = pd.MultiIndex.from_tuples(columns_tuples, names=[f"Header {len(header_rows)-i}" for i in range(len(header_rows))])
        # Level is descending from len(header_rows) to 1

    else:
        # join by '\n' if there are multiple lines
        column_headers = [' \\n'.join([row[i] for row in header_rows if row[i]]) for i in range(num_columns)]




    # note: header rows will be taken out
    table._df = pd.DataFrame(data=table_array, columns=column_headers)
    
    # a. mark as projecting/non-projecting
    if projecting_indices:
        is_projecting = [x in projecting_indices for x in range(num_rows)]
        # remove the header_indices
        # note that ditr._determine_headers_and_projecting 
        # automatically makes is_projecting and header_indices mutually exclusive
        table._projecting_indices = [i for i, x in enumerate(is_projecting) if x]
    
    # b. drop the former header rows always
    table._df.drop(index=header_indices, inplace=True)

    # c. drop the empty rows
    table._df.drop(index=empty_rows, inplace=True)
    table._df.reset_index(drop=True, inplace=True)
    
    table.outliers = outliers
    return table._df

