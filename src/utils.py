import logging
from src.config import STANDARD_FIELDS

def detect_region(filename: str) -> str:
    """Detect region from filename."""
    filename = filename.lower()
    if "north" in filename:
        return "north"
    elif "south" in filename:
        return "south"
    elif "east" in filename:
        return "east"
    else:
        return "unknown"

def transform_row(raw_row: dict, mapping: dict, default_region: str, row_num: int) -> dict:
    """Transform a raw row to standard format."""
    standard = {field: "" for field in STANDARD_FIELDS}

    for raw_key, standard_key in mapping.items():
        if raw_key in raw_row and raw_key != "region_default":
            standard[standard_key] = raw_row[raw_key]

    if not standard.get("region"):
        standard["region"] = default_region

    if not standard.get("salesperson"):
        standard["salesperson"] = mapping.get("salesperson.default", "Unknown")

    try:
        standard["quantity"] = int(float(standard.get("quantity", 0)))
    except (ValueError, TypeError):
        bad_qty = standard.get("quantity")
        standard["quantity"] = 0
        logging.warning(f"Invalid quantity in row {row_num}: {bad_qty}")

    try:
        standard["revenue"] = round(float(standard.get("revenue", 0.0)), 2)
    except (ValueError, TypeError):
        bad_rev = standard.get("revenue")
        standard["revenue"] = 0.0
        logging.warning(f"Invalid revenue in row {row_num}: {bad_rev}")
        
    return standard