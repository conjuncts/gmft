from abc import ABC, abstractmethod

import pandas as pd

from gmft.core.ml.prediction import TablePredictions
from gmft.pdf_bindings.base import BasePage
from gmft.detectors.base import CroppedTable, RotatedCroppedTable


class FormattedTable(RotatedCroppedTable):
    """
    A table with header and data information.
    Can be converted into df, csv, etc.

    Warning: This class is not meant to be instantiated directly. Use a :class:`.TableFormatter` to convert a :class:`.CroppedTable` to a :class:`.FormattedTable`.
    """

    predictions: TablePredictions

    def __init__(self, cropped_table: CroppedTable, df: pd.DataFrame = None):
        self._df = df

        if cropped_table is None:
            # this is a tough position, but assume that
            # the user will handle CroppedTable.__init__ themselves
            # and that they know what they are doing (trying to subclass FormattedTable)
            self._img = None
            self._img_dpi = None
            self._img_padding = None
            self._img_margin = None
            self._word_height = None
            self._captions = None
            return

        # create shallow copy
        if "angle" in cropped_table.__dict__:
            angle = cropped_table.angle
        else:
            angle = 0
        super().__init__(
            page=cropped_table.page,
            bbox=cropped_table.rect.bbox,
            confidence_score=cropped_table.confidence_score,
            angle=angle,
            label=cropped_table.label,
        )

        self._img = (
            cropped_table._img.copy() if cropped_table._img is not None else None
        )
        self._img_dpi = cropped_table._img_dpi
        self._img_padding = cropped_table._img_padding
        self._img_margin = cropped_table._img_margin
        self._word_height = cropped_table._word_height
        self._captions = cropped_table._captions

    def df(self, recalculate=False, config_overrides=None) -> pd.DataFrame:
        """
        Return the table as a pandas dataframe (cached).

        :param recalculate:
            Force a recompute.
            It is preferred to explicitly call recompute().
        """
        return self._df

    def recompute(self, config=None) -> pd.DataFrame:
        """
        Recompute the internal dataframe.
        This WILL modify internal state/cache.
        """
        self._df = self.to_pandas(config=config)
        return self._df

    def to_pandas(self, config=None) -> pd.DataFrame:
        """
        Return the table as a pandas dataframe (uncached).

        This will NOT modify internal state/cache.
        """
        return self._df

    @abstractmethod
    def visualize(self):
        """
        Visualize the table.
        """
        # raise NotImplementedError
        return self.image()

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


class BaseFormatter(ABC):
    """
    Abstract class for converting a :class:`.CroppedTable` to a :class:`.FormattedTable`.
    Allows export to csv, df, etc.
    """

    @abstractmethod
    def extract(self, table: CroppedTable) -> FormattedTable:
        """
        Extract the data from the table.
        Produces a :class:`.FormattedTable` instance, from which data can be exported in csv, html, etc.
        """
        raise NotImplementedError

    def format(self, table: CroppedTable, **kwargs) -> FormattedTable:
        """
        Alias for :meth:`extract`.
        """
        return self.extract(table, **kwargs)


class TableFormatter(BaseFormatter):
    pass


def _normalize_bbox(
    bbox: tuple[float, float, float, float],
    used_scale_factor: float,
    used_padding: tuple[float, float],
    used_margin: tuple[float, float] = None,
):
    """
    Normalize bbox such that:
    1. padding is removed (so (0, 0) is the top-left of the cropped table)
    2. scale factor is normalized (dpi=72)
    3. margin is removed (so (0, 0) is the start of the original detected bbox)
    """
    if used_margin is None:
        used_margin = (0, 0)
    bbox = [
        bbox[0] - used_padding[0],
        bbox[1] - used_padding[1],
        bbox[2] - used_padding[0],
        bbox[3] - used_padding[1],
    ]
    bbox = [
        bbox[0] / used_scale_factor,
        bbox[1] / used_scale_factor,
        bbox[2] / used_scale_factor,
        bbox[3] / used_scale_factor,
    ]
    bbox = [
        bbox[0] - used_margin[0],
        bbox[1] - used_margin[1],
        bbox[2] - used_margin[0],
        bbox[3] - used_margin[1],
    ]
    return bbox
