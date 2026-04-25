def count_items(tree: dict) -> dict:
    counts = {
        "directories": 0,
        "files": 0,
    }

    def walk(node: dict):
        if node["type"] == "directory":
            counts["directories"] += 1

            for child in node.get("children", []):
                walk(child)
        else:
            counts["files"] += 1

    walk(tree)
    return counts
