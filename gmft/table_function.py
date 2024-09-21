"""
Module containing methods of formatting tables: structural analysis, data extraction, and converting them into pandas dataframes.

This module formerly contained the table format logic. While you may still import from this module, the logic has since been moved to :py:mod:`gmft.formatters.common` and :py:mod:`gmft.formatters.tatr`.

Whenever possible, classes (like :class:`AutoTableFormatter`) should be imported from gmft.auto, not from this module.

Example:
    >>> from gmft.auto import AutoTableFormatter
"""

from gmft.formatters.common import FormattedTable, TableFormatter, _normalize_bbox
from gmft.formatters.tatr import TATRFormatConfig, TATRFormattedTable, TATRFormatter

TATRTableFormatter = TATRFormatter