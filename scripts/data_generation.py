"""Generate synthetic regional sales CSV datasets."""

import csv
from pathlib import Path
import random

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PRODUCTS = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"]


def generate_all(records_per_region: int = 100) -> None:
    # North region
    with open(DATA_DIR / "north_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Product", "Quantity", "Revenue", "Rep"])
        for _ in range(records_per_region):
            writer.writerow([
                random.choice(PRODUCTS),
                random.randint(1, 20),
                round(random.uniform(50, 1500), 2),
                f"Rep_{random.randint(1, 5)}",
            ])

    # South region
    with open(DATA_DIR / "south_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Region", "Salesperson", "Product", "Units", "Total"])
        for _ in range(int(records_per_region * 0.8)):
            writer.writerow([
                "South",
                f"Agent_{random.randint(1, 4)}",
                random.choice(PRODUCTS),
                random.randint(1, 15),
                round(random.uniform(40, 1200), 2),
            ])

    # East region
    with open(DATA_DIR / "east_sales.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Qty", "Price"])
        for _ in range(int(records_per_region * 1.2)):
            writer.writerow([
                random.choice(PRODUCTS),
                random.randint(1, 25),
                round(random.uniform(30, 1000), 2),
            ])

    print(f"Sales datasets generated successfully in '{DATA_DIR}'.")


if __name__ == "__main__":
    generate_all()