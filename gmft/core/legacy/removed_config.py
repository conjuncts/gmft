from typing_extensions import deprecated


class LegacyRemovedConfig:
    """
    This class contains legacy configuration settings that will soon be removed.
    """

    # ---- deprecated ----
    # aggregate_spanning_cells = False
    @property
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def aggregate_spanning_cells(self):
        raise DeprecationWarning(
            "aggregate_spanning_cells has been removed. Will break in v0.6.0."
        )

    @aggregate_spanning_cells.setter
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def aggregate_spanning_cells(self, value):
        raise DeprecationWarning(
            "aggregate_spanning_cells has been removed. Will break in v0.6.0."
        )

    # corner_clip_outlier_threshold = 0.1
    # """"corner clip" is when the text is clipped by a corner, and not an edge"""
    @property
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def corner_clip_outlier_threshold(self):
        raise DeprecationWarning(
            "corner_clip_outlier_threshold has been removed. Will break in v0.6.0."
        )

    @corner_clip_outlier_threshold.setter
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def corner_clip_outlier_threshold(self, value):
        raise DeprecationWarning(
            "corner_clip_outlier_threshold has been removed. Will break in v0.6.0."
        )

    # spanning_cell_minimum_width = 0.6
    @property
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def spanning_cell_minimum_width(self):
        raise DeprecationWarning(
            "spanning_cell_minimum_width has been removed. Will break in v0.6.0."
        )

    @spanning_cell_minimum_width.setter
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def spanning_cell_minimum_width(self, value):
        raise DeprecationWarning(
            "spanning_cell_minimum_width has been removed. Will break in v0.6.0."
        )

    @property
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def deduplication_iob_threshold(self):
        raise DeprecationWarning(
            "deduplication_iob_threshold is deprecated. See nms_overlap_threshold instead. Will break in v0.6.0."
        )

    @deduplication_iob_threshold.setter
    @deprecated("This config setting is unused and will be removed in v0.6.0")
    def deduplication_iob_threshold(self, value):
        raise DeprecationWarning(
            "deduplication_iob_threshold is deprecated. See nms_overlap_threshold instead. Will break in v0.6.0."
        )
