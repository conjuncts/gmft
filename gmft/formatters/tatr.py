import copy
from typing import List, Union

from gmft.core._dataclasses import non_defaults_only, with_config
from gmft.core.io.serial.dicts import _extract_fctn_results, _extract_indices
from gmft.core.legacy.fctn_results import LegacyFctnResults
from gmft.core.ml import _resolve_device
from gmft.core.ml.prediction import (
    BboxPrediction,
    _empty_effective_predictions,
    _empty_indices_predictions,
)
from gmft.detectors.base import CroppedTable, RotatedCroppedTable
from gmft.impl.tatr.config import TATRFormatConfig
from gmft.formatters.base import FormattedTable, TableFormatter, _normalize_bbox
from gmft.pdf_bindings.base import BasePage
import torch


from gmft.algorithm.structure import extract_to_df
from gmft.table_visualization import plot_results_unwr


class TATRFormattedTable(FormattedTable, LegacyFctnResults):
    """
    FormattedTable, as seen by a Table Transformer (TATR).
    See :class:`.TATRTableFormatter`.
    """

    _POSSIBLE_ROWS = [
        "table row",
        "table spanning cell",
        "table projected row header",
    ]  # , 'table column header']
    _POSSIBLE_PROJECTING_ROWS = [
        "table projected row header"
    ]  # , 'table spanning cell']
    _POSSIBLE_COLUMN_HEADERS = ["table column header"]
    _POSSIBLE_COLUMNS = ["table column"]
    id2label = {
        0: "table",
        1: "table column",
        2: "table row",
        3: "table column header",
        4: "table projected row header",
        5: "table spanning cell",
        6: "no object",
    }
    label2id = {v: k for k, v in id2label.items()}

    config: TATRFormatConfig
    outliers: dict[str, bool]

    def __init__(
        self,
        cropped_table: CroppedTable,
        fctn_results: dict,
        config: TATRFormatConfig = None,
    ):
        super(TATRFormattedTable, self).__init__(cropped_table)
        self.predictions = {
            "tatr": fctn_results,
            "effective": _empty_effective_predictions(),
            "indices": _empty_indices_predictions(),
        }

        if config is None:
            config = TATRFormatConfig()
        self.config = config
        self.outliers = None

    def df(self, recalculate=False, config_overrides: TATRFormatConfig = None):
        """
        Return the table as a pandas dataframe.
        :param recalculate: by default, the dataframe is cached
        :param config_overrides: override the config settings for this call only
        """
        if (
            recalculate == False and config_overrides is None and self._df is not None
        ):  # cache
            return self._df

        config = with_config(self.config, config_overrides)

        return self.recompute(config=config)

    def recompute(self, config: TATRFormatConfig):
        """
        Recompute the internal dataframe.
        """
        self._df = extract_to_df(self, config=config)
        return self._df

    def visualize(
        self,
        filter=None,
        dpi=None,
        padding=None,
        margin=(10, 10, 10, 10),
        effective=False,
        return_img=True,
        **kwargs,
    ):
        """
        Visualize the table.

        :param filter: filter the labels to visualize. See TATRFormattedTable.id2label
        :param dpi: Sets the dpi. If none, then the dpi of the cached image is used.
        :param padding: padding around the table. If None, then the padding of the cached image is used.
        :param margin: margin around the table. If None, then the margin of the cached image is used.
        :param effective: if True, visualize the effective rows and columns, which may differ from the table transformer's output.
        :param return_img: if True, return the image. If False, the matplotlib figure is plotted.
        """
        if dpi is None:
            dpi = self._img_dpi
        if dpi is None:
            dpi = 72

        scale_by = dpi / 72

        if effective:
            if self._df is None:
                self._df = self.df()
            vis: List[BboxPrediction] = [
                item
                for sublist in self.predictions["effective"].values()
                for item in sublist
            ]
            boxes = [x["bbox"] for x in vis]
            boxes = [(x * scale_by for x in bbox) for bbox in boxes]
            _to_visualize = {
                "scores": [x["confidence"] for x in vis],
                "labels": [self.label2id[x["label"]] for x in vis],
                "boxes": boxes,
            }
        else:
            # transform functionalized coordinates into image coordinates
            boxes = [
                (x * scale_by for x in bbox)
                for bbox in self.predictions["tatr"]["boxes"]
            ]

            _to_visualize = {
                "scores": self.predictions["tatr"]["scores"],
                "labels": self.predictions["tatr"]["labels"],
                "boxes": boxes,
            }

        # get needed scale factor and dpi
        img = self.image(dpi=dpi, padding=padding, margin=margin)
        true_margin = [x * (dpi / 72) for x in self._img_margin]
        return plot_results_unwr(
            img,
            _to_visualize["scores"],
            _to_visualize["labels"],
            _to_visualize["boxes"],
            TATRFormattedTable.id2label,
            filter=filter,
            padding=padding,
            margin=true_margin,
            return_img=return_img,
            **kwargs,
        )

    def to_dict(self):
        """
        Serialize self into dict
        """
        if self.angle != 0:
            parent = RotatedCroppedTable.to_dict(self)
        else:
            parent = CroppedTable.to_dict(self)
        optional = {}
        if self.predictions["indices"]:
            optional["predictions.indices"] = self.predictions["indices"]
        return {
            **parent,
            **{
                "config": non_defaults_only(self.config),
                "outliers": self.outliers,
                "fctn_results": self.predictions["tatr"],
            },
            **optional,
        }

    @staticmethod
    def from_dict(d: dict, page: BasePage):
        """
        Deserialize from dict.
        A page is required partly because of memory management, since having this open a page may cause memory issues.
        """
        d = copy.deepcopy(d)  # don't modify the original dict
        cropped_table = CroppedTable.from_dict(d, page)

        results = _extract_fctn_results(d)
        config = TATRFormatConfig(**d["config"])

        table = TATRFormattedTable(
            cropped_table,
            results,
            config=config,
        )
        table.outliers = d.get("outliers", None)
        table.predictions["indices"] = _extract_indices(d)
        return table


class TATRFormatter(TableFormatter):
    """
    Uses a TableTransformerForObjectDetection for small/medium tables, and a custom algorithm for large tables.

    Using :meth:`extract`, a :class:`.FormattedTable` is produced, which can be exported to csv, df, etc.
    """

    def __init__(self, config: TATRFormatConfig = None):
        import transformers
        from transformers import AutoImageProcessor, TableTransformerForObjectDetection

        if config is None:
            config = TATRFormatConfig()
        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)

        if not config.warn_uninitialized_weights:
            previous_verbosity = transformers.logging.get_verbosity()
            transformers.logging.set_verbosity(transformers.logging.ERROR)
        self.image_processor = AutoImageProcessor.from_pretrained(
            config.image_processor_path
        )
        revision = "no_timm" if config.no_timm else None
        self.structor = TableTransformerForObjectDetection.from_pretrained(
            config.formatter_path, revision=revision
        ).to(_resolve_device(config.torch_device))
        self.config = config
        if not config.warn_uninitialized_weights:
            transformers.logging.set_verbosity(previous_verbosity)

    def extract(
        self,
        table: CroppedTable,
        dpi=144,
        padding="auto",
        margin=None,
        config_overrides=None,
    ) -> TATRFormattedTable:
        """
        Extract the data from the table.
        """

        config = with_config(self.config, config_overrides)

        image = table.image(dpi=dpi, padding=padding, margin=margin)  # (20, 20, 20, 20)
        padding = table._img_padding
        margin = table._img_margin

        scale_factor = dpi / 72
        encoding = self.image_processor(image, return_tensors="pt").to(
            _resolve_device(self.config.torch_device)
        )
        with torch.no_grad():
            outputs = self.structor(**encoding)

        target_sizes = [image.size[::-1]]
        # threshold = 0.3
        # note that a LOW threshold is good because the model is overzealous in
        # but since we find the highest-intersecting row, same-row elements still tend to stay together
        # this is better than having a high threshold, because if we have fewer rows than expected, we merge cells
        # losing information
        results = self.image_processor.post_process_object_detection(
            outputs,
            threshold=config.formatter_base_threshold,
            target_sizes=target_sizes,
        )[0]

        # create a new FormattedTable instance with the cropped table and the dataframe

        # return formatted_table
        results = {k: v.tolist() for k, v in results.items()}

        # normalize results w.r.t. padding and scale factor
        for i, bbox in enumerate(results["boxes"]):
            results["boxes"][i] = _normalize_bbox(
                bbox,
                used_scale_factor=scale_factor,
                used_padding=padding,
                used_margin=margin,
            )

        formatted_table = TATRFormattedTable(
            table,
            results,
            config=config,
        )
        return formatted_table


# legacy aliases
TATRTableFormatter = TATRFormatter

__all__ = [
    "TATRFormatConfig",
    "TATRFormattedTable",
    "TATRFormatter",
    "TATRFormattedTable.from_dict",
    "TATRFormattedTable.to_dict",
]
