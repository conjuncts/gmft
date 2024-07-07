## v0.2.0-pre

- Return visualized images as PIL image; allow padding or margin around visualized

Several tweaks to formatting algorithm that may result in different outputs compared to prior versions.
- Automatically drop rows whose only non-null values is the "is_projecting_row" column
- Fill in gaps between table rows, so hopefully no text is skipped
- ^ TODO: in that case, try the large table assumption
- Non-maxima suppression, as seen in inference.py
- Widen out the rows to same length, as seen in inference.py
- Several tweaks to conditions, parameters, heuristics

## v0.1.1

- Created AutoTableFormatter and AutoTableDetector for future flexibility

## v0.1.0

- Added support for rotated tables (since v0.0.4)
- Even better accuracy for large tables
- Renamed is_spanning_row to is_projecting_row