## v0.2.0-pre

- Automatically drop rows whose only non-null values is the "is_projecting_row" column
- Return visualized images as PIL image
- Fill in gaps between table rows, so hopefully no text is skipped
- ^ TODO: in that case, try the large table assumption

## v0.1.1

- Created AutoTableFormatter and AutoTableDetector for future flexibility

## v0.1.0

- Added support for rotated tables (since v0.0.4)
- Even better accuracy for large tables
- Renamed is_spanning_row to is_projecting_row