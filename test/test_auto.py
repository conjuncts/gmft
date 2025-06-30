"""Tests for the auto module's lazy loading behavior."""

import pytest
from gmft.auto import (
    AutoTableDetector,
    AutoTableFormatter,
    AutoFormatConfig,
)
from gmft.detectors.tatr import TATRDetector
from gmft.formatters.tatr import TATRFormatter
from gmft.impl.tatr.config import TATRFormatConfig


def test_auto_table_detector_instantiation():
    """Test that AutoTableDetector properly instantiates as TATRDetector."""
    detector = AutoTableDetector()
    assert isinstance(detector, TATRDetector)


def test_auto_table_formatter_instantiation():
    """Test that AutoTableFormatter properly instantiates as TATRFormatter."""
    formatter = AutoTableFormatter()
    assert isinstance(formatter, TATRFormatter)


def test_auto_format_config_instantiation():
    """Test that AutoFormatConfig properly instantiates as TATRFormatConfig."""
    config = AutoFormatConfig()
    assert isinstance(config, TATRFormatConfig)
