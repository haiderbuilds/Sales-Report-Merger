import csv
import random

# Sample products
products = ["Laptop", "Mouse", "Keyboard", "Monitor","Headphones"]

# Generate north region sales report
with open("north_sales.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Product", "Quantity", "Revenue", "Rep"])
    for _ in range(100):
        writer.writerow([
            random.choice(products),
            random.randint(1, 20),
            round(random.uniform(50, 1500), 2),
            f"Rep_{random.randint(1,5)}"
        ])

# Generate south region report
with open("south_sales.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Region", "Salesperson", "Product", "Units", "Total"])
    for _ in range(80):
        writer.writerow([
            "South",
            f"Agent_{random.randint(1, 4)}",
            random.choice(products),
            random.randint(1, 15),
            round(random.uniform(40, 1200), 2)
        ])

# Generate east region report
with open("east_sales.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Item", "Qty", "Price"])
    for _ in range(120):
        writer.writerow([
            random.choice(products),
            random.randint(1, 25),
            round(random.uniform(30, 1000), 2)
        ])
print("Data files generated successfully!")