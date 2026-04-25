from __future__ import annotations

from typing import Any


def build_tree_text(tree: dict[str, Any]) -> str:
    lines: list[str] = []

    def walk(node: dict[str, Any], prefix: str = "", is_last: bool = True) -> None:
        name = node.get("name", "")
        node_type = node.get("type", "file")
        children = node.get("children", [])

        connector = "└── " if is_last else "├── "

        if prefix == "":
            lines.append(name + ("/" if node_type == "directory" else ""))
        else:
            lines.append(prefix + connector + name + ("/" if node_type == "directory" else ""))

        if not children:
            return

        next_prefix = prefix + ("    " if is_last else "│   ")
        for index, child in enumerate(children):
            child_is_last = index == len(children) - 1
            walk(child, next_prefix, child_is_last)

    walk(tree)
    return "\n".join(lines)
