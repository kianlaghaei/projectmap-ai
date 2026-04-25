def parse_comma_separated_items(value: str) -> set[str]:
    return {
        item.strip()
        for item in value.split(",")
        if item.strip()
    }
