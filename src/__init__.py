"""Sales report consolidation and normalization toolkit."""

from .config import FIELD_MAPPINGS, STANDARD_FIELDS
from .processor import merge_sales_reports
from .utils import detect_region, transform_row, validate_row, write_summary

__version__ = "0.1.0"

__all__ = [
    "merge_sales_reports",
    "detect_region",
    "transform_row",
    "validate_row",
    "write_summary",
    "FIELD_MAPPINGS",
    "STANDARD_FIELDS"
]