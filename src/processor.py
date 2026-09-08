import csv
import logging
from collections.abc import Iterator, Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any

from .config import FIELD_MAPPINGS, STANDARD_FIELDS
from .utils import detect_region, transform_row, validate_row, write_summary

logger = logging.getLogger(__name__)


def _configure_logging(log_file: str | Path | None) -> None:
    """Attach a single UTF-8 file handler without creating duplicates on repeated calls."""
    if not log_file:
        return

    resolved_path = Path(log_file).resolve()
    handler_name = f"file_handler_{resolved_path.name}"

    if any(handler.name == handler_name for handler in logger.handlers):
        return

    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(resolved_path, encoding="utf-8")
    handler.name = handler_name
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def _process_file(file_path: Path) -> Iterator[dict[str, Any]]:
    """Yield transformed and validated rows from a single regional sales file."""
    region_key = detect_region(file_path.name)
    logger.info("Processing: %s (Region: %s)", file_path, region_key)

    mapping = FIELD_MAPPINGS.get(region_key, {})
    default_region = mapping.get(
        "region_default",
        region_key.title() if region_key != "unknown" else "Unknown",
    )

    try:
        with file_path.open("r", newline="", encoding="utf-8") as in_f:
            reader = csv.DictReader(in_f)

            for row_num, raw_row in enumerate(reader, start=2):
                row = transform_row(raw_row, mapping, default_region, row_num)

                if not validate_row(row, row_num):
                    continue

                row["region"] = str(row["region"]).strip().title()
                yield row

    except (OSError, csv.Error) as err:
        logger.error("Failed to read or parse file %s: %s", file_path, err)


def merge_sales_reports(
    input_files: Sequence[str | Path],
    output_file: str | Path,
    summary_file: str | Path,
    log_file: str | Path | None = None,
    retain_in_memory: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Merge and normalize regional CSV sales reports into a single consolidated output.

    Args:
        input_files: File paths to input sales CSVs.
        output_file: Target path for the consolidated output CSV.
        summary_file: Target path for the aggregated summary CSV.
        log_file: Optional file destination for process logs.
        retain_in_memory: When True, returns all parsed rows in memory to preserve
            API compatibility; set to False for multi-gigabyte datasets to run in O(1) RAM.

    Returns:
        A tuple of (consolidated_rows, region_stats).
    """
    _configure_logging(log_file)

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    summary_path = Path(summary_file)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    region_stats: dict[str, dict[str, Any]] = {
        region.title(): {"revenue": Decimal("0.00"), "transactions": 0, "products": {}}
        for region in FIELD_MAPPINGS
    }

    consolidated: list[dict[str, Any]] = []
    total_written = 0

    with out_path.open("w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=STANDARD_FIELDS)
        writer.writeheader()

        for filepath in input_files:
            file_path = Path(filepath)

            if not file_path.is_file():
                logger.error("Skipping missing or non-file input path: %s", filepath)
                continue

            for row in _process_file(file_path):
                writer.writerow(row)
                total_written += 1

                if retain_in_memory:
                    consolidated.append(row)

                region = row["region"]
                stats = region_stats.setdefault(
                    region,
                    {"revenue": Decimal("0.00"), "transactions": 0, "products": {}},
                )
                
                stats["revenue"] += row["revenue"]
                stats["transactions"] += 1
                
                product = row["product"]
                stats["products"][product] = (
                    stats["products"].get(product, 0) + row["quantity"]
                )

    write_summary(str(summary_path), region_stats, total_written)
    logger.info("Merged %d rows into %s", total_written, out_path)

    return consolidated, region_stats