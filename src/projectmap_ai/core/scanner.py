from __future__ import annotations

from pathlib import Path
from typing import Any

from projectmap_ai.config import ScanConfig


def build_node(
    path: Path,
    config: ScanConfig,
    current_depth: int = 0,
) -> dict[str, Any] | None:
    """
    Recursively build a directory/file tree node.

    Output shape:
    {
        "name": "src",
        "path": "/abs/path/src",
        "type": "directory" | "file",
        "children": [...]
    }
    """
    try:
        if not path.exists():
            return None

        if not config.include_hidden and path.name.startswith(".") and current_depth != 0:
            return None

        if path.is_dir():
            if path.name in config.ignored_dirs and current_depth != 0:
                return None

            node: dict[str, Any] = {
                "name": path.name if current_depth != 0 else path.resolve().name,
                "path": str(path.resolve()),
                "type": "directory",
                "children": [],
            }

            if config.max_depth is not None and current_depth >= config.max_depth:
                return node

            children: list[dict[str, Any]] = []
            try:
                items = sorted(
                    path.iterdir(),
                    key=lambda p: (not p.is_dir(), p.name.lower()),
                )
            except PermissionError:
                return node

            for child in items:
                if child.is_symlink() and not config.follow_symlinks:
                    continue

                child_node = build_node(
                    child,
                    config=config,
                    current_depth=current_depth + 1,
                )
                if child_node is not None:
                    children.append(child_node)

            node["children"] = children
            return node

        if path.is_file():
            if path.name in config.ignored_files:
                return None

            if not config.include_hidden and path.name.startswith("."):
                return None

            return {
                "name": path.name,
                "path": str(path.resolve()),
                "type": "file",
            }

    except PermissionError:
        return None
    except OSError:
        return None

    return None


def scan_project(config: ScanConfig) -> dict[str, Any]:
    root = config.normalized_root()
    node = build_node(root, config=config, current_depth=0)
    if node is None:
        raise ValueError(f"Could not scan path: {root}")
    return node
