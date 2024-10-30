## v0.4.0

Features: 3 new table structure recognition options!
- Added `TabledFormatter`, with support of the fantastic new [Tabled](https://github.com/VikParuchuri/tabled/) library from VikParuchuri. Check out the [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/example_tabled_compat.ipynb) for a quick example.
- Added `HistogramFormatter`, a super-fast and decently accurate algorithmic option for table structure recognition. The algorithm uses word bboxes to detect separating lines between text. Check out the [demo notebook](https://github.com/conjuncts/gmft/blob/main/notebooks/example_histogram.ipynb) for a quick example.
    - A visual to explain `HistogramFormatter`:

![](https://github.com/conjuncts/gmft/blob/main/docs/source/images/histogram_expl.png?raw=true)

- Added `DITRFormatter`. This formatter is a blend between TATRFormatter and HistogramFormatter, being trained to recognize table separating lines rather than cells. It fine tunes `microsoft/table-transformer-structure-recognition-v1.1-all` on PubTables-1M for 15 epochs. Its main draw is mixing and matching deep and algorithmic separating line detection.

These formatters can all be used in combination with any detector (like TATRDetector).

Bugfixes:
- Tweaked spanning cell merging
    - Fixed bug where it would overwrite data
- Give warning when importing from `gmft` directly (use `gmft.auto` instead)
- Merged PR #32, thanks!


## v0.3.2

Changes:
- Raise default threshold of heuristic for rejecting tables on high overlap. Makes ValueErrors more rare.
    - (total_overlap_reject_threshold) ValueError thrown on overlap > 90%, up from 20%
    - (total_overlap_warn_threshold) overlap warned on overlap > 10%, up from 5%
- Python 3.9 compatability.

## v0.3.1

Bugfix:
- divide by 0 when taking median of empty list in row height estimate
- Fix broken build in v0.3.0 (missing formatters)

Changes:
- Added `Img2TableDetector`.
- refactor of code into organizational modules, `detectors` and `formatters`
- Importing from `gmft` is no longer encouraged. Please import from `gmft.auto` instead.
- Tentative rich_text module and FormattedPage for direct RAG embedding usage
- Configs are now dataclasses. However, a possibly breaking change is that **passing `config_overrides` will now completely replace the config**, rather than updating it.



## v0.2.2

- `is_projecting_row` is removed, with the information now available under `FormattedTable._projecting_indices`
- Formally removed `timm` as a dependency
- Slight tweak to captions with the aim to better reflect paragraph word height, still WIP. See #8 and be93159
- Fix: return result so image can be used outside of notebook by @brycedrennan in https://github.com/conjuncts/gmft/pull/15

**Full Changelog**: https://github.com/conjuncts/gmft/compare/v0.2.1...v0.2.2

## v0.2.1

- GPU support, thank you @MathiasToftas!

## v0.2.0

### Features:
- Multiple headers; multi-index tables
- Spanning cells on both the top and left
- Captions for tables
- "Margin" parameter allows text outside of table bbox to be included
- Return visualized images as PIL image; allow padding or margin around visualized

### Several tweaks to formatting algorithm that may result in different outputs compared to prior versions.
- Automatically drop rows whose only non-null values is the "is_projecting_row" column
- Fill in gaps between table rows, to reduce skipped text
- Non-maxima suppression, as seen in inference.py
    - "total overlap" metric has become less useful in favor of "rows removed by NMS"
- Widen out the rows to same length
- Several tweaks to conditions, parameters, heuristics
    - superscripts/subscripts now more likely to be merged to their parent rows

### Many possibly breaking changes to config.
- `TableDetectorConfig.confidence_score_threshold` has been renamed to `TableDetectorConfig.detector_base_threshold`
- `TableFormatter.deduplication_iob_threshold` has been removed in favor of `nms_iob_threshold`
- `spanning_cell_minimum_width`, `corner_clip_outlier_threshold`, and `aggregate_spanning_cells` have been removed
- Tweaks to default settings may yield different results



## v0.1.1


Older:
- Created AutoTableFormatter and AutoTableDetector for future flexibility (v0.1.1, a840488)
- Renamed is_spanning_row to is_projecting_row (v0.1.1, a840488)
- Added support for rotated tables (v0.0.4, 5aeb80d)
- Even better accuracy for large tables (v0.1.0, 8c537ed)

