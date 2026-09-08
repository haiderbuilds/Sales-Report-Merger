import csv
import logging
from collections import Counter
from decimal import Decimal, InvalidOperation
from .config import STANDARD_FIELDS

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
        if raw_key in raw_row and not raw_key.endswith("_default"):
            standard[standard_key] = raw_row[raw_key]

    if not standard.get("region"):
        standard["region"] = default_region or mapping.get("region_default", "Unknown")

    if not standard.get("salesperson"):
        standard["salesperson"] = mapping.get("salesperson_default", "Unknown")

    raw_quantity = standard.get("quantity")
    try:
        standard["quantity"] = int(float(raw_quantity)) if raw_quantity not in ("", None) else 0
    except (ValueError, TypeError):
        standard["quantity"] = 0
        logging.warning(f"Invalid quantity in row {row_num}: {raw_quantity}")

    raw_revenue = standard.get("revenue")
    try:
        standard["revenue"] = Decimal(str(raw_revenue)) if raw_revenue not in ("", None) else Decimal("0.00")
    except (InvalidOperation, ValueError, TypeError):
        standard["revenue"] = Decimal("0.00")
        logging.warning(f"Invalid revenue in row {row_num}: {raw_revenue}")

    return standard

def validate_row(row: dict, row_num: int) -> bool:
    """Validate a standard row."""
    product = str(row.get("product") or "").strip()
    if not product:
        logging.warning(f"Row {row_num}: missing product")
        return False

    quantity = row.get("quantity", 0)
    if quantity is None or quantity <= 0:
        logging.warning(f"Row {row_num}: invalid quantity {quantity}")
        return False
    revenue = row.get("revenue", 0.0)
    if revenue is None or revenue <= 0:
        logging.warning(f"Row {row_num}: invalid revenue {revenue}")
        return False

    return True

def write_summary(summary_file: str, stats: dict, total_rows: int):
    """Write the summary dashboard."""
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["Sales summary dashboard."])
        writer.writerow([])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Transactions", total_rows])
        writer.writerow([])

        writer.writerow(["Region", "Total Revenue", "Transactions", "Avg Order Value"])
        for region, data in stats.items():
            transactions = data.get("transactions", 0)
            revenue = data.get("revenue", 0.0)
            avg = round(revenue / transactions, 2) if transactions > 0 else 0.0
            writer.writerow([region, f"${revenue:,.2f}", transactions, f"${avg:,.2f}"])

        writer.writerow([])

        writer.writerow(["Region Top Products"])
        writer.writerow([])
        for region, data in stats.items():
            writer.writerow([f"--- {region} ---"])
            products = Counter(data.get("products", {}))
            for product, qty in products.most_common(3):
                writer.writerow([product, qty])
            writer.writerow([])

        writer.writerow(["Overall Top Products"])
        all_products = Counter()
        for region, data in stats.items():
            all_products.update(data.get("products", {}))

        for product, qty in all_products.most_common(5):
            writer.writerow([product, qty])