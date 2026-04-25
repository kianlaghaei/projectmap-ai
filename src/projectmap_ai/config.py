from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".next",
    ".nuxt",
    ".cache",
    ".dart_tool",
    "coverage",
    "target",
    ".terraform",
}

DEFAULT_IGNORED_FILES = {
    ".DS_Store",
    "Thumbs.db",
}


@dataclass
class ScanConfig:
    root_path: Path
    ignored_dirs: set[str] = field(default_factory=lambda: set(DEFAULT_IGNORED_DIRS))
    ignored_files: set[str] = field(default_factory=lambda: set(DEFAULT_IGNORED_FILES))
    include_hidden: bool = False
    max_depth: int | None = None
    follow_symlinks: bool = False

    def normalized_root(self) -> Path:
        return self.root_path.expanduser().resolve()
