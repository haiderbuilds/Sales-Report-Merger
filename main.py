"""Pipeline entry point to generate raw data and compile consolidated sales reports."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

from src import merge_sales_reports

# Base directory paths
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"


def ensure_datasets_exist(target_files: list[Path]) -> None:
    """Generate regional data if any expected input file is missing."""
    missing = [f for f in target_files if not f.is_file()]
    if not missing:
        return

    print(f"Missing {len(missing)} dataset(s). Running data generator...")
    try:
        from scripts.data_generation import generate_all
        generate_all(records_per_region=100)
    except ImportError:
        # Fallback if data_generation.py hasn't been refactored into generate_all() yet
        import subprocess
        script_path = ROOT_DIR / "scripts" / "data_generation.py"
        subprocess.run([sys.executable, str(script_path)], check=True)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_files = [
        DATA_DIR / "north_sales.csv",
        DATA_DIR / "south_sales.csv",
        DATA_DIR / "east_sales.csv",
    ]

    # 1. Ensure input datasets are available without forced overwrites
    try:
        ensure_datasets_exist(input_files)
    except Exception as err:
        logging.error("Failed to generate required datasets: %s", err)
        return 1

    # 2. Output destinations
    consolidated_csv = OUTPUT_DIR / "consolidated_sales.csv"
    summary_csv = OUTPUT_DIR / "summary_dashboard.csv"
    log_file = OUTPUT_DIR / "merge_errors.log"

    # 3. Execute report consolidation
    print("\nConsolidating regional sales datasets...")
    consolidated_rows, region_stats = merge_sales_reports(
        input_files=input_files,
        output_file=consolidated_csv,
        summary_file=summary_csv,
        log_file=log_file,
    )

    if not consolidated_rows:
        print("[!] No rows were successfully processed. Check merge_errors.log.", file=sys.stderr)
        return 1

    # 4. Display executive summary breakdown
    print("\n" + "=" * 55)
    print(f"{'Region':<10} | {'Transactions':>14} | {'Revenue':>15}")
    print("-" * 55)
    for region, data in sorted(region_stats.items()):
        rev = data.get("revenue", 0)
        tx = data.get("transactions", 0)
        print(f"{region:<10} | {tx:>14,d} | ${rev:>14,.2f}")
    print("=" * 55)

    print(f"\nPipeline finished successfully:")
    print(f"  • Rows Processed : {len(consolidated_rows)}")
    print(f"  • Merged Output  : {consolidated_csv.relative_to(ROOT_DIR)}")
    print(f"  • Summary Report : {summary_csv.relative_to(ROOT_DIR)}")
    print(f"  • Processing Log : {log_file.relative_to(ROOT_DIR)}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())