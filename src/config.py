STANDARD_FIELDS = [
    "region",
    "product",
    "quantity",
    "revenue",
    "salesperson"
]

FIELD_MAPPINGS = {
    "north": {
        "Product": "product",
        "Quantity": "quantity",
        "Revenue": "revenue",
        "Rep": "salesperson",
        "region_default": "North"
    },
    "south": {
        "Region": "region",
        "Salesperson": "salesperson",
        "Product": "product",
        "Units": "quantity",
        "Total": "revenue",
        "region_default": "South"
    },
    "east": {
        "Item": "product",
        "Qty": "quantity",
        "Price": "revenue",
        "region_default": "East",
        "salesperson_default": "Unknown"
    }
}