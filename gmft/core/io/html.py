from gmft.algorithm.structure_rewrite import _execute_cell_merges, export_header
from gmft.reformat.schema import CellMergerType, TableStructureWithArray


def _build_cell(
    content, row_idx, col_idx, colspans, rowspans, tag="td", indent="      "
):
    """
    Build an HTML cell (th or td) with proper colspan/rowspan attributes

    Args:
        content: The cell content
        row_idx: Row index for lookup in colspan/rowspan dicts
        col_idx: Column index for lookup in colspan/rowspan dicts
        colspan: Dictionary mapping (row, col) to colspan values
        rowspan: Dictionary mapping (row, col) to rowspan values
        tag: HTML tag to use ("th" or "td")
        indent: Indentation string for the cell
    """
    escaped_content = _escape_html(content) if content is not None else ""

    cell_builder = f"{indent}<{tag}"
    if (row_idx, col_idx) in colspans:
        colspan_value = colspans[(row_idx, col_idx)]
        rowspan_value = rowspans[(row_idx, col_idx)]
        if colspan_value > 1:
            cell_builder += f' colspan="{colspan_value}"'
        if rowspan_value > 1:
            cell_builder += f' rowspan="{rowspan_value}"'
    cell_builder += f">{escaped_content}</{tag}>"

    return cell_builder


def _to_html(
    struct: TableStructureWithArray, *, enable_multi_header=True, attempt_span=True
):
    """
    Produce the html version of the table
    """

    # Example of merge schema:
    # struct.merges[0]['merger']
    # == (2, 1, 7, 1, CellMergerType.REPEAT)
    # == (row_min, col_min, row_max, col_max, dtype)

    if attempt_span:
        struct = _execute_cell_merges(
            struct,
            _dtype_override=(CellMergerType.PUSH_BACKWARD | CellMergerType.AGGREGATE),
        )

    header_indices = struct.header_rows
    table_array = struct.table_array

    merges = [merge["merger"] for merge in struct.merges]
    # we pay attention to certain (row_min, col_min) values
    colspans = {}
    rowspans = {}

    # other cells need to be skipped. TODO: surely there is a better algorithm for this
    # TODO: problem with overlapping ranges
    silenced = set()
    for merge in merges:
        colspans[(merge.row_min, merge.col_min)] = merge.col_max - merge.col_min + 1
        rowspans[(merge.row_min, merge.col_min)] = merge.row_max - merge.row_min + 1

        # this doesn't feel right, but oh well
        for row in range(merge.row_min, merge.row_max + 1):
            for col in range(merge.col_min, merge.col_max + 1):
                silenced.add((row, col))
        silenced.remove((merge.row_min, merge.col_min))  # always show the top-left cell

    if not table_array:
        return "<table></table>"

    # Get column headers
    column_headers = export_header(
        struct, enable_multi_header=enable_multi_header, enable_pandas=False
    )

    # Filter out header rows from table data
    data_rows = [row for i, row in enumerate(table_array) if i not in header_indices]

    html_parts = ["<table>"]

    # Re-unzip
    reunzipped = list(zip(*column_headers))

    # Add header if we have one
    # if column_headers:
    html_parts.append("  <thead>")
    for row_idx, column_headers in enumerate(reunzipped):
        html_parts.append("    <tr>")
        for col_idx, header in enumerate(column_headers):
            # Escape HTML characters and handle None values
            if (row_idx, col_idx) in silenced:
                continue
            cell_content = _build_cell(
                header, row_idx, col_idx, colspans, rowspans, tag="th"
            )
            html_parts.append(cell_content)
        html_parts.append("    </tr>")
    html_parts.append("  </thead>")

    # Add body
    num_headers = len(reunzipped)
    if data_rows:
        html_parts.append("  <tbody>")
        for row_uncorrected, row in enumerate(data_rows):
            html_parts.append("    <tr>")
            row_idx = row_uncorrected + num_headers
            for col_idx, cell in enumerate(row):
                # Escape HTML characters and handle None values
                if (row_idx, col_idx) in silenced:
                    continue
                cell_content = _build_cell(
                    cell, row_idx, col_idx, colspans, rowspans, tag="td"
                )
                html_parts.append(cell_content)
            html_parts.append("    </tr>")
        html_parts.append("  </tbody>")

    html_parts.append("</table>")

    return "\n".join(html_parts)


def _escape_html(text):
    """
    Escape HTML special characters in text
    """
    if text is None:
        return ""

    # Convert to string if not already
    text = str(text)

    # Replace HTML special characters
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")

    return text
