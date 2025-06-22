import copy
from typing import Optional
from gmft.core.ml.prediction import (
    IndicesPredictions,
    RawBboxPredictions,
    _empty_indices_predictions,
)
from gmft.detectors.base import CroppedTable
from gmft.formatters.base import _normalize_bbox
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.pdf_bindings.base import BasePage


def _extract_fctn_results(d: dict) -> RawBboxPredictions:
    """
    Extract prediction["tatr"], formerly known as fctn_results
    """
    if "fctn_results" not in d:
        raise ValueError(
            "fctn_results not found in dict -- dict may be a CroppedTable but not a TATRFormattedTable."
        )

    results = d["fctn_results"]  # fix shallow copy issue
    if (
        "fctn_scale_factor" in d
        or "scale_factor" in d
        or "fctn_padding" in d
        or "padding" in d
    ):
        # deprecated: this is for backwards compatibility
        scale_factor = d.get("fctn_scale_factor", d.get("scale_factor", 1))
        padding = d.get("fctn_padding", d.get("padding", (0, 0)))
        padding = tuple(padding)

        # normalize results here
        for i, bbox in enumerate(results["boxes"]):
            results["boxes"][i] = _normalize_bbox(
                bbox, used_scale_factor=scale_factor, used_padding=padding
            )
    return results


def _extract_indices(d: dict) -> IndicesPredictions:
    # version gmft>=0.5 format
    if "predictions.indices" in d:
        return d["predictions.indices"]

    # version gmft<0.5 format
    if any(
        x in d
        for x in ["_hier_left_indices", "_top_header_indices", "_projecting_indices"]
    ):
        return {
            "_projecting": d.get("_projecting_indices"),
            "_hier_left": d.get("_hier_left_indices"),
            "_top_header": d.get("_top_header_indices"),
        }

    return _empty_indices_predictions()
