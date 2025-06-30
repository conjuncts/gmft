from gmft.core.ml.prediction import (
    RawBboxPredictions,
    EffectivePredictions,
    TablePredictions,
)
from typing_extensions import deprecated


class LegacyFctnResults:
    """
    Small class to re-route old
    """

    predictions: TablePredictions

    @property
    @deprecated("Use self.predictions.tatr")
    def fctn_results(self) -> RawBboxPredictions:
        return self.predictions.tatr

    @fctn_results.setter
    @deprecated("Use self.predictions.tatr")
    def fctn_results(self, value: RawBboxPredictions):
        self.predictions.tatr = value

    @property
    @deprecated("Use self.predictions.effective")
    def effective_rows(self):
        return self.predictions.effective["rows"]

    @effective_rows.setter
    @deprecated("Use self.predictions.effective")
    def effective_rows(self, value):
        self.predictions.effective["rows"] = value

    @property
    @deprecated("Use self.predictions.effective")
    def effective_columns(self):
        return self.predictions.effective["columns"]

    @effective_columns.setter
    @deprecated("Use self.predictions.effective")
    def effective_columns(self, value):
        self.predictions.effective["columns"] = value

    @property
    @deprecated("Use self.predictions.effective")
    def effective_headers(self):
        return self.predictions.effective["headers"]

    @effective_headers.setter
    @deprecated("Use self.predictions.effective")
    def effective_headers(self, value):
        self.predictions.effective["headers"] = value

    @property
    @deprecated("Use self.predictions.effective")
    def effective_projecting(self):
        return self.predictions.effective["projecting"]

    @effective_projecting.setter
    @deprecated("Use self.predictions.effective")
    def effective_projecting(self, value):
        self.predictions.effective["projecting"] = value

    @property
    @deprecated("Use self.predictions.effective")
    def effective_spanning(self):
        return self.predictions.effective["spanning"]

    @effective_spanning.setter
    @deprecated("Use self.predictions.effective")
    def effective_spanning(self, value):
        self.predictions.effective["spanning"] = value

    @property
    @deprecated("Use self.predictions.indices['top_header']")
    def _top_header_indices(self):
        return self.predictions.indices.get("top_header")

    @_top_header_indices.setter
    @deprecated("Use self.predictions.indices['_top_header']")
    def _top_header_indices(self, value):
        self.predictions.indices["_top_header"] = value

    @property
    @deprecated("Use self.predictions.indices['_projecting']")
    def _projecting_indices(self):
        return self.predictions.indices.get("_projecting")

    @_projecting_indices.setter
    @deprecated("Use self.predictions.indices['_projecting']")
    def _projecting_indices(self, value):
        self.predictions.indices["_projecting"] = value

    @property
    @deprecated("Use self.predictions.indices['_hier_left']")
    def _hier_left_indices(self):
        return self.predictions.indices.get("_hier_left")

    @_hier_left_indices.setter
    @deprecated("Use self.predictions.indices['hier_left']")
    def _hier_left_indices(self, value):
        self.predictions.indices["hier_left"] = value
