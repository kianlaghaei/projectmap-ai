from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from projectmap_ai.config import DEFAULT_IGNORED_DIRS, DEFAULT_IGNORED_FILES, ScanConfig
from projectmap_ai.core.json_exporter import export_json
from projectmap_ai.core.scanner import scan_project
from projectmap_ai.core.stats import calculate_stats
from projectmap_ai.core.tree_builder import build_tree_text


class ProjectMapApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ProjectMap AI")
        self.root.geometry("1100x760")
        self.root.minsize(900, 650)

        self.selected_path = tk.StringVar()
        self.format_var = tk.StringVar(value="both")
        self.include_hidden_var = tk.BooleanVar(value=False)
        self.follow_symlinks_var = tk.BooleanVar(value=False)
        self.max_depth_var = tk.StringVar(value="")
        self.stats_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        self._build_path_section(main_frame)
        self._build_options_section(main_frame)
        self._build_actions_section(main_frame)
        self._build_output_section(main_frame)
        self._build_status_section(main_frame)

    def _build_path_section(self, parent: ttk.Frame) -> None:
        path_frame = ttk.LabelFrame(parent, text="Project Path", padding=10)
        path_frame.pack(fill="x", pady=(0, 10))

        entry = ttk.Entry(path_frame, textvariable=self.selected_path)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side="left")

    def _build_options_section(self, parent: ttk.Frame) -> None:
        options_frame = ttk.LabelFrame(parent, text="Options", padding=10)
        options_frame.pack(fill="x", pady=(0, 10))

        left = ttk.Frame(options_frame)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right = ttk.Frame(options_frame)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Ignored Directories (comma-separated):").pack(anchor="w")
        self.ignored_dirs_text = tk.Text(left, height=5, wrap="word")
        self.ignored_dirs_text.pack(fill="x", expand=True, pady=(4, 8))
        self.ignored_dirs_text.insert("1.0", ", ".join(sorted(DEFAULT_IGNORED_DIRS)))

        ttk.Label(left, text="Ignored Files (comma-separated):").pack(anchor="w")
        self.ignored_files_text = tk.Text(left, height=3, wrap="word")
        self.ignored_files_text.pack(fill="x", expand=True, pady=(4, 0))
        self.ignored_files_text.insert("1.0", ", ".join(sorted(DEFAULT_IGNORED_FILES)))

        ttk.Label(right, text="Output Format:").pack(anchor="w")
        format_combo = ttk.Combobox(
            right,
            textvariable=self.format_var,
            values=["tree", "json", "both"],
            state="readonly",
        )
        format_combo.pack(fill="x", pady=(4, 12))
        format_combo.current(2)

        ttk.Checkbutton(
            right,
            text="Include hidden files/folders",
            variable=self.include_hidden_var,
        ).pack(anchor="w", pady=(0, 8))

        ttk.Checkbutton(
            right,
            text="Follow symbolic links",
            variable=self.follow_symlinks_var,
        ).pack(anchor="w", pady=(0, 8))

        ttk.Label(right, text="Max Depth (optional):").pack(anchor="w")
        ttk.Entry(right, textvariable=self.max_depth_var).pack(fill="x", pady=(4, 0))

    def _build_actions_section(self, parent: ttk.Frame) -> None:
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(actions_frame, text="Generate Map", command=self.generate_output).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions_frame, text="Copy Output", command=self.copy_output).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions_frame, text="Save Output", command=self.save_output).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(actions_frame, text="Clear", command=self.clear_output).pack(side="left")

    def _build_output_section(self, parent: ttk.Frame) -> None:
        output_frame = ttk.LabelFrame(parent, text="Output", padding=10)
        output_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(output_frame, wrap="none", undo=True)
        self.output_text.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        y_scroll.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=y_scroll.set)

    def _build_status_section(self, parent: ttk.Frame) -> None:
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x")

        ttk.Label(status_frame, textvariable=self.stats_var).pack(anchor="w")

    def browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.selected_path.set(folder)

    def _parse_csv_text(self, text_widget: tk.Text) -> set[str]:
        raw = text_widget.get("1.0", "end").strip()
        if not raw:
            return set()
        return {item.strip() for item in raw.split(",") if item.strip()}

    def _parse_max_depth(self) -> int | None:
        value = self.max_depth_var.get().strip()
        if not value:
            return None
        try:
            depth = int(value)
            if depth < 0:
                raise ValueError
            return depth
        except ValueError:
            raise ValueError("Max Depth must be a non-negative integer.")

    def generate_output(self) -> None:
        path_str = self.selected_path.get().strip()
        if not path_str:
            messagebox.showwarning("Missing Path", "Please select a project folder.")
            return

        path = Path(path_str)
        if not path.exists() or not path.is_dir():
            messagebox.showerror("Invalid Path", "The selected path is not a valid directory.")
            return

        try:
            max_depth = self._parse_max_depth()
            config = ScanConfig(
                root_path=path,
                ignored_dirs=self._parse_csv_text(self.ignored_dirs_text),
                ignored_files=self._parse_csv_text(self.ignored_files_text),
                include_hidden=self.include_hidden_var.get(),
                max_depth=max_depth,
                follow_symlinks=self.follow_symlinks_var.get(),
            )

            tree = scan_project(config)
            tree_text = build_tree_text(tree)
            json_text = export_json(tree)
            stats = calculate_stats(tree)

            fmt = self.format_var.get().strip().lower()
            if fmt == "tree":
                output = tree_text
            elif fmt == "json":
                output = json_text
            else:
                output = f"=== TREE ===\n{tree_text}\n\n=== JSON ===\n{json_text}"

            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", output)

            self.stats_var.set(
                f"Directories: {stats['directories']} | "
                f"Files: {stats['files']} | "
                f"Total Nodes: {stats['total_nodes']}"
            )

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def copy_output(self) -> None:
        content = self.output_text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("No Content", "There is no output to copy.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        messagebox.showinfo("Copied", "Output copied to clipboard.")

    def save_output(self) -> None:
        content = self.output_text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("No Content", "There is no output to save.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Output",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            Path(file_path).write_text(content, encoding="utf-8")
            messagebox.showinfo("Saved", f"Output saved to:\n{file_path}")
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))

    def clear_output(self) -> None:
        self.output_text.delete("1.0", "end")
        self.stats_var.set("Ready")


def run_app() -> None:
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    app = ProjectMapApp(root)
    root.mainloop()
