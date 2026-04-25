from pathlib import Path


def should_ignore(path: Path, ignore_dirs: set[str], ignore_files: set[str]) -> bool:
    if path.is_dir() and path.name in ignore_dirs:
        return True

    if path.is_file() and path.name in ignore_files:
        return True

    return False


def scan_project(
    root_path: Path,
    ignore_dirs: set[str],
    ignore_files: set[str],
) -> dict:
    def walk(current_path: Path) -> dict:
        node = {
            "name": current_path.name,
            "type": "directory" if current_path.is_dir() else "file",
            "path": str(current_path),
        }

        if current_path.is_dir():
            children = []

            try:
                entries = sorted(
                    current_path.iterdir(),
                    key=lambda item: (item.is_file(), item.name.lower())
                )

                for entry in entries:
                    if should_ignore(entry, ignore_dirs, ignore_files):
                        continue

                    children.append(walk(entry))

            except PermissionError:
                node["error"] = "Permission denied"

            node["children"] = children

        return node

    return walk(root_path)
