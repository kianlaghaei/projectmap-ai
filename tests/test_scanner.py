from pathlib import Path

from projectmap_ai.config import ScanConfig
from projectmap_ai.core.scanner import scan_project


def test_scan_project_basic(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "README.md").write_text("# test", encoding="utf-8")

    config = ScanConfig(root_path=tmp_path)
    tree = scan_project(config)

    assert tree["type"] == "directory"
    assert tree["name"] == tmp_path.name

    children_names = {child["name"] for child in tree["children"]}
    assert "src" in children_names
    assert "README.md" in children_names


def test_scan_project_ignores_directory(tmp_path: Path) -> None:
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text("x", encoding="utf-8")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text("print(1)", encoding="utf-8")

    config = ScanConfig(root_path=tmp_path)
    tree = scan_project(config)

    children_names = {child["name"] for child in tree["children"]}
    assert "node_modules" not in children_names
    assert "app" in children_names
