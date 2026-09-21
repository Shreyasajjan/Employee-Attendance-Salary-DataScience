"""Utility functions for the Employee Attendance & Salary Data Science project."""

from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATABASE_DIR = PROJECT_ROOT / "data" / "database"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

for folder in [DATA_RAW, DATA_PROCESSED, DATABASE_DIR, MODELS_DIR, OUTPUTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def validate_non_negative(value, field_name):
    """Raise ValueError when a numeric value is negative."""
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative: {value}")
    return True


def safe_divide(numerator, denominator):
    """Return zero when denominator is zero."""
    return numerator / denominator if denominator else 0.0
