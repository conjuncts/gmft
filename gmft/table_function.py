"""
Module containing methods of formatting tables: structural analysis, data extraction, and converting them into pandas dataframes.

Whenever possible, classes (like :class:`AutoTableFormatter`) should be imported from the top-level module, not from this module,
as the exact paths may change in future versions.

Example:
    >>> from gmft import AutoTableFormatter
"""


from abc import ABC, abstractmethod
import copy

from gmft.pdf_bindings.common import BasePage
import torch

from gmft.table_detection import CroppedTable, RotatedCroppedTable

import transformers
from transformers import AutoImageProcessor, TableTransformerForObjectDetection
import pandas as pd

from gmft.table_function_algorithm import extract_to_df
from gmft.table_visualization import plot_results_unwr



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
    
    force_large_table_assumption=None
    """True: force large table assumption to be applied to all tables
    False: force large table assumption to not be applied to any tables
    None: heuristically apply large table assumption according to threshold and overlap"""


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
            vis = self.effective_rows + self.effective_columns + self.effective_headers
            boxes = [x['bbox'] for x in vis]
            boxes = [(x * scale_by for x in bbox) for bbox in boxes]
            _to_visualize = {
                "scores": [x['confidence'] for x in vis],
                "labels": [self.label2id[x['label']] for x in vis],
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
        return plot_results_unwr(img, _to_visualize['scores'], _to_visualize['labels'], _to_visualize['boxes'], TATRFormattedTable.id2label, filter=filter, **kwargs)
            
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
        Deserialize from dict.
        A page is required partly because of memory management, since having this open a page may cause memory issues.
        """
        cropped_table = CroppedTable.from_dict(d, page)
        
        if 'fctn_results' not in d:
            raise ValueError("fctn_results not found in dict -- dict may be a CroppedTable but not a TATRFormattedTable.")
        
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
    

def _normalize_bbox(bbox: tuple[float, float, float, float], used_scale_factor: float, used_padding: tuple[float, float]):
    """
    Normalize bbox such that:
    1. padding is removed (so (0, 0) is the top-left of the cropped table)
    2. scale factor is normalized (dpi=72)
    """
    bbox = [bbox[0] - used_padding[0], bbox[1] - used_padding[1], bbox[2] - used_padding[0], bbox[3] - used_padding[1]]
    bbox = [bbox[0] / used_scale_factor, bbox[1] / used_scale_factor, bbox[2] / used_scale_factor, bbox[3] / used_scale_factor]
    return bbox
        