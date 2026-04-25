from __future__ import annotations

from pathlib import Path


def normalize_path(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()
