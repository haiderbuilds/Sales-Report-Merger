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

