from __future__ import annotations

from typing import Any


def calculate_stats(tree: dict[str, Any]) -> dict[str, int]:
    stats = {
        "directories": 0,
        "files": 0,
        "total_nodes": 0,
    }

    def walk(node: dict[str, Any]) -> None:
        stats["total_nodes"] += 1

        node_type = node.get("type")
        if node_type == "directory":
            stats["directories"] += 1
            for child in node.get("children", []):
                walk(child)
        elif node_type == "file":
            stats["files"] += 1

    walk(tree)
    return stats
