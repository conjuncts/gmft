import pytest

from gmft.table_detection import TableDetector
from gmft.table_function import TATRTableFormatter


@pytest.fixture
def detector():
    return TableDetector()

@pytest.fixture
def formatter():
    return TATRTableFormatter()