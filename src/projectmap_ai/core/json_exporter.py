import json


def build_json_text(tree: dict) -> str:
    return json.dumps(tree, ensure_ascii=False, indent=2)
