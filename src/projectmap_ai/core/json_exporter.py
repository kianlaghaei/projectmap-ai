from __future__ import annotations

import json
from typing import Any


def export_json(tree: dict[str, Any], indent: int = 2) -> str:
    return json.dumps(tree, ensure_ascii=False, indent=indent)
