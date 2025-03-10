from gmft.detectors.base import (
    position_words,
    CroppedTable,
    BaseDetector,
    RotatedCroppedTable,
)
from gmft.detectors.tatr import TATRDetector, TableDetectorConfig, TableDetector
import warnings

# legacy file; have been moved to corresponding locations.

TATRTableDetector = TATRDetector

warnings.warn(
    "Importing from gmft.table_detection is deprecated. Please import from gmft.detectors.base or gmft.detectors.tatr instead.", 
    DeprecationWarning
)
