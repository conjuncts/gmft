"""
Module containing methods of formatting tables: structural analysis, data extraction, and converting them into pandas dataframes.

Whenever possible, classes (like :class:`AutoTableFormatter`) should be imported from the top-level module, not from this module,
as the exact paths may change in future versions.

Example:
    >>> from gmft import AutoTableFormatter
"""

from gmft.formatters.common import FormattedTable, TableFormatter, _normalize_bbox
from gmft.formatters.tatr import TATRFormatConfig, TATRFormattedTable, TATRTableFormatter