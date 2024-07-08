## v0.2.0rc1

### Features:
- Multiple headers; multi-index tables
- Spanning cells on both the top and left
- "Margin" parameter allows text outside of table bbox to be included
- Return visualized images as PIL image; allow padding or margin around visualized

### Several tweaks to formatting algorithm that may result in different outputs compared to prior versions.
- Automatically drop rows whose only non-null values is the "is_projecting_row" column
- Fill in gaps between table rows, so hopefully no text is skipped
- Non-maxima suppression, as seen in inference.py
    - "total overlap" metric has become less useful in favor of "rows removed by NMS"
- Widen out the rows to same length
- Several tweaks to conditions, parameters, heuristics

### Many possibly breaking changes to config.
- `TableDetectorConfig.confidence_score_threshold` has been renamed to `TableDetectorConfig.detector_base_threshold`
- `TableFormatter.deduplication_iob_threshold` has been removed in favor of `nms_iob_threshold`
- `spanning_cell_minimum_width`, `corner_clip_outlier_threshold`, and `aggregate_spanning_cells` have been removed
- Tweaks to default settings may yield different results



## v0.1.1

- Created AutoTableFormatter and AutoTableDetector for future flexibility

## v0.1.0

- Added support for rotated tables (since v0.0.4)
- Even better accuracy for large tables
- Renamed is_spanning_row to is_projecting_row