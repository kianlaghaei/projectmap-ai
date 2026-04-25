def build_tree_text(tree: dict) -> str:
    lines = []

    def walk(node: dict, prefix: str = "", is_last: bool = True):
        name = node["name"]

        if node["type"] == "directory":
            name += "/"

        if prefix == "":
            lines.append(name)
        else:
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")

        children = node.get("children", [])

        next_prefix = prefix + ("    " if is_last else "│   ")

        for index, child in enumerate(children):
            walk(child, next_prefix, index == len(children) - 1)

    walk(tree)
    return "\n".join(lines)
