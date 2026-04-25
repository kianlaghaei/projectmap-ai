from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from projectmap_ai.config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_FILES,
)
from projectmap_ai.core.scanner import scan_project
from projectmap_ai.core.tree_builder import build_tree_text
from projectmap_ai.core.json_exporter import build_json_text
from projectmap_ai.core.stats import count_items
from projectmap_ai.utils.path_utils import parse_comma_separated_items


class ProjectMapAIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1000x700")

        self.selected_path = tk.StringVar()
        self.output_format = tk.StringVar(value="tree")

        self.ignore_dirs = tk.StringVar(
            value=", ".join(sorted(DEFAULT_IGNORE_DIRS))
        )
        self.ignore_files = tk.StringVar(
            value=", ".join(sorted(DEFAULT_IGNORE_FILES))
        )

        self._build_ui()

    def run(self):
        self.root.mainloop()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        path_frame = ttk.LabelFrame(main_frame, text="Project Path", padding=10)
        path_frame.pack(fill="x")

        path_input = ttk.Entry(path_frame, textvariable=self.selected_path)
        path_input.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_button = ttk.Button(
            path_frame,
            text="Browse",
            command=self._browse_folder
        )
        browse_button.pack(side="left")

        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill="x", pady=10)

        ttk.Label(options_frame, text="Ignore Directories").pack(anchor="w")
        ttk.Entry(options_frame, textvariable=self.ignore_dirs).pack(
            fill="x",
            pady=(0, 8)
        )

        ttk.Label(options_frame, text="Ignore Files").pack(anchor="w")
        ttk.Entry(options_frame, textvariable=self.ignore_files).pack(
            fill="x",
            pady=(0, 8)
        )

        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill="x")

        ttk.Label(format_frame, text="Output Format:").pack(
            side="left",
            padx=(0, 10)
        )

        ttk.Radiobutton(
            format_frame,
            text="Tree Text",
            variable=self.output_format,
            value="tree"
        ).pack(side="left")

        ttk.Radiobutton(
            format_frame,
            text="JSON",
            variable=self.output_format,
            value="json"
        ).pack(side="left")

        ttk.Radiobutton(
            format_frame,
            text="Both",
            variable=self.output_format,
            value="both"
        ).pack(side="left")

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            actions_frame,
            text="Scan Project",
            command=self._scan_project
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="Copy Output",
            command=self._copy_output
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="Save Output",
            command=self._save_output
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="Clear",
            command=self._clear_output
        ).pack(side="left")

        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(anchor="w", pady=(0, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(
            output_frame,
            wrap="none",
            font=("Consolas", 10)
        )
        self.output_text.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(
            output_frame,
            orient="vertical",
            command=self.output_text.yview
        )
        scrollbar_y.pack(side="right", fill="y")

        self.output_text.configure(yscrollcommand=scrollbar_y.set)

    def _browse_folder(self):
        folder = filedialog.askdirectory()

        if folder:
            self.selected_path.set(folder)

    def _scan_project(self):
        path_value = self.selected_path.get().strip()

        if not path_value:
            messagebox.showwarning("Warning", "Please select a project folder.")
            return

        root_path = Path(path_value)

        if not root_path.exists() or not root_path.is_dir():
            messagebox.showerror("Error", "Selected path is not a valid directory.")
            return

        ignore_dirs = parse_comma_separated_items(self.ignore_dirs.get())
        ignore_files = parse_comma_separated_items(self.ignore_files.get())

        try:
            tree = scan_project(
                root_path=root_path,
                ignore_dirs=ignore_dirs,
                ignore_files=ignore_files,
            )

            tree_output = build_tree_text(tree)
            json_output = build_json_text(tree)

            selected_format = self.output_format.get()

            if selected_format == "tree":
                output = tree_output
            elif selected_format == "json":
                output = json_output
            else:
                output = (
                    "===== TREE STRUCTURE =====\n"
                    f"{tree_output}\n\n"
                    "===== JSON STRUCTURE =====\n"
                    f"{json_output}"
                )

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output)

            stats = count_items(tree)

            self.status_label.config(
                text=(
                    "Scanned successfully | "
                    f"Directories: {stats['directories']} | "
                    f"Files: {stats['files']}"
                )
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Failed to scan project:\n{error}"
            )

    def _copy_output(self):
        content = self.output_text.get("1.0", tk.END).strip()

        if not content:
            messagebox.showinfo("Info", "Nothing to copy.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()

        messagebox.showinfo("Success", "Output copied to clipboard.")

    def _save_output(self):
        content = self.output_text.get("1.0", tk.END).strip()

        if not content:
            messagebox.showinfo("Info", "Nothing to save.")
            return

        extension = ".json" if self.output_format.get() == "json" else ".txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("Markdown files", "*.md"),
                ("All files", "*.*"),
            ],
            title="Save Output"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            messagebox.showinfo("Success", "Output saved successfully.")

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Failed to save file:\n{error}"
            )

    def _clear_output(self):
        self.output_text.delete("1.0", tk.END)
        self.status_label.config(text="Ready")
