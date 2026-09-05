import csv
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
            avg = round(revenue / transactions if transactions > 0 else 0.0, 2)
            writer.writerow([region, f"${revenue:,.2f}", transactions, f"${avg:,.2f}"])

        writer.writerow([])

        writer.writerow(["Region Top Products"])
        writer.writerow([])
        for region, data in stats.items():
            writer.writerow([f"--- {region} ---"])
            products = data.get("products", {})
            top_products = sorted(products.items(), key=lambda x: x[1], reverse=True)[:3]
            for product, qty in top_products:
                writer.writerow([product, qty])
            writer.writerow([])

        writer.writerow(["Overall Top Products"])
        all_products = {}
        for region, data in stats.items():
            for product, qty in data.get("products", {}).items():
                all_products[product] = all_products.get(product, 0) + qty

        top_all = sorted(all_products.items(), key=lambda x: x[1], reverse=True)[:5]
        for product, qty in top_all:
            writer.writerow([product, qty])