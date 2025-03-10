"""
Module containing methods of formatting tables: structural analysis, data extraction, and converting them into pandas dataframes.

This module formerly contained the table format logic. While you may still import from this module, the logic has since been moved to :py:mod:`gmft.formatters.base` and :py:mod:`gmft.formatters.tatr`.

Whenever possible, classes (like :class:`AutoTableFormatter`) should be imported from gmft.auto, not from this module.

Example:
    >>> from gmft.auto import AutoTableFormatter
"""

from gmft.formatters.base import FormattedTable, TableFormatter, _normalize_bbox
from gmft.formatters.tatr import TATRFormatConfig, TATRFormattedTable, TATRFormatter
import warnings

TATRTableFormatter = TATRFormatter

warnings.warn(
    "Importing from gmft.table_function is deprecated. Please import from gmft.formatters.base or gmft.formatters.tatr instead."
)