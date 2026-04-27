from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from projectmap_ai.config import DEFAULT_IGNORED_DIRS, DEFAULT_IGNORED_FILES, ScanConfig
from projectmap_ai.core.json_exporter import export_json
from projectmap_ai.core.scanner import scan_project
from projectmap_ai.core.stats import calculate_stats
from projectmap_ai.core.tree_builder import build_tree_text


DARK_STYLESHEET = """
QWidget {
    background-color: #0b0f14;
    color: #edf2f7;
    font-size: 13px;
    font-family: "Segoe UI", Vazirmatn, Tahoma, sans-serif;
}

QMainWindow {
    background-color: #0b0f14;
}

QFrame#Card {
    background-color: #141a22;
    border: 1px solid #263141;
    border-radius: 16px;
}

QLabel#Title {
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
}

QLabel#Subtitle {
    font-size: 13px;
    color: #93a4b8;
}

QLabel#SectionTitle {
    font-size: 16px;
    font-weight: 800;
    color: #7dd3fc;
}

QLineEdit, QComboBox, QPlainTextEdit {
    background-color: #0f1621;
    border: 1px solid #2b394d;
    border-radius: 10px;
    padding: 9px 11px;
    color: #f8fafc;
    selection-background-color: #0ea5e9;
}

QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1px solid #38bdf8;
    background-color: #0b1220;
}

QPushButton {
    background-color: #1b2635;
    border: 1px solid #33445d;
    border-radius: 10px;
    padding: 10px 14px;
    color: #f8fafc;
    font-weight: 700;
}

QPushButton:hover {
    background-color: #243449;
    border-color: #4b6383;
}

QPushButton:pressed {
    background-color: #182234;
}

QPushButton#PrimaryButton {
    background-color: #0f9f6e;
    border: 1px solid #22c55e;
    color: #ffffff;
}

QPushButton#PrimaryButton:hover {
    background-color: #12b981;
}

QPushButton#PrimaryButton:pressed {
    background-color: #0d8f63;
}

QTabWidget::pane {
    border: 1px solid #263141;
    border-radius: 10px;
    background: #0f1621;
    top: -1px;
}

QTabBar::tab {
    background: #141a22;
    color: #aec0d4;
    border: 1px solid #2b394d;
    padding: 9px 16px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #0f1621;
    color: #7dd3fc;
    border-bottom-color: #0f1621;
}

QTabBar::tab:hover:!selected {
    background: #1b2635;
    color: #f8fafc;
}

QToolBar {
    background: #0b0f14;
    border-bottom: 1px solid #202b39;
    spacing: 10px;
    padding: 8px 10px;
}

QStatusBar {
    background: #0b0f14;
    color: #93a4b8;
    border-top: 1px solid #202b39;
}

QCheckBox {
    spacing: 8px;
}

QSplitter::handle {
    background-color: #263141;
    width: 4px;
    border-radius: 2px;
    margin: 0 4px;
}

QSplitter::handle:hover {
    background-color: #38bdf8;
}

QScrollArea {
    border: none;
    background: transparent;
}

QComboBox QAbstractItemView {
    background-color: #0f1621;
    color: #f8fafc;
    border: 1px solid #2b394d;
    selection-background-color: #0ea5e9;
}

QScrollBar:vertical {
    background: #0b0f14;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #263141;
    min-height: 28px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background: #38bdf8;
}
"""


class Card(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setFrameShape(QFrame.StyledPanel)


class ProjectMapMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ProjectMap AI")
        self.setMinimumSize(760, 520)

        self.tree_output = ""
        self.json_output = ""
        self.combined_output = ""

        self._build_ui()
        self._build_toolbar()
        self._build_statusbar()
        self._fit_to_screen()

    def _fit_to_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(1200, 760)
            return

        available = screen.availableGeometry()
        width = min(1400, max(760, int(available.width() * 0.86)))
        height = min(900, max(520, int(available.height() * 0.86)))
        self.resize(width, height)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        header = self._create_header()
        root_layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setMinimumWidth(320)
        left_scroll.setMaximumWidth(520)
        left_scroll.setWidget(self._create_left_panel())

        splitter.addWidget(left_scroll)
        splitter.addWidget(self._create_right_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([390, 900])

        root_layout.addWidget(splitter, 1)

    def _create_header(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)

        title = QLabel("ProjectMap AI")
        title.setObjectName("Title")

        subtitle = QLabel("Modern project structure explorer with Tree / JSON export")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return card

    def _create_left_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self._create_path_card())
        layout.addWidget(self._create_options_card())
        layout.addWidget(self._create_action_card())
        layout.addStretch(1)

        return container

    def _create_path_card(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = self._section_title("Project Path")

        row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setMinimumWidth(0)
        self.path_input.setPlaceholderText("Select project folder...")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_folder)

        row.addWidget(self.path_input, 1)
        row.addWidget(browse_btn)

        layout.addWidget(title)
        layout.addLayout(row)
        return card

    def _create_options_card(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = self._section_title("Scan Options")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["tree", "json", "both"])
        self.format_combo.setCurrentText("both")

        self.max_depth_input = QLineEdit()
        self.max_depth_input.setPlaceholderText("Optional, e.g. 3")

        self.include_hidden_checkbox = QCheckBox("Include hidden files / folders")
        self.follow_symlinks_checkbox = QCheckBox("Follow symbolic links")

        self.ignored_dirs_edit = QPlainTextEdit()
        self.ignored_dirs_edit.setPlaceholderText("Ignored directories, comma-separated")
        self.ignored_dirs_edit.setPlainText(", ".join(sorted(DEFAULT_IGNORED_DIRS)))
        self.ignored_dirs_edit.setFixedHeight(92)

        self.ignored_files_edit = QPlainTextEdit()
        self.ignored_files_edit.setPlaceholderText("Ignored files, comma-separated")
        self.ignored_files_edit.setPlainText(", ".join(sorted(DEFAULT_IGNORED_FILES)))
        self.ignored_files_edit.setFixedHeight(76)

        form.addRow("Output Format", self.format_combo)
        form.addRow("Max Depth", self.max_depth_input)
        form.addRow("", self.include_hidden_checkbox)
        form.addRow("", self.follow_symlinks_checkbox)
        form.addRow("Ignored Dirs", self.ignored_dirs_edit)
        form.addRow("Ignored Files", self.ignored_files_edit)

        layout.addLayout(form)
        return card

    def _create_action_card(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = self._section_title("Actions")

        self.generate_btn = QPushButton("Generate Map")
        self.generate_btn.setObjectName("PrimaryButton")
        self.generate_btn.setMinimumHeight(42)
        self.generate_btn.clicked.connect(self.generate_output)

        self.copy_btn = QPushButton("Copy Current Tab")
        self.copy_btn.clicked.connect(self.copy_output)

        self.save_btn = QPushButton("Save Current Tab")
        self.save_btn.clicked.connect(self.save_output)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_output)

        layout.addWidget(title)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.clear_btn)
        return card

    def _create_right_panel(self) -> QWidget:
        card = Card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title = self._section_title("Output")

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tree_editor = self._create_output_editor()
        self.json_editor = self._create_output_editor()
        self.combined_editor = self._create_output_editor()

        self.tabs.addTab(self.tree_editor, "Tree")
        self.tabs.addTab(self.json_editor, "JSON")
        self.tabs.addTab(self.combined_editor, "Combined")

        self.stats_label = QLabel("Ready")
        self.stats_label.setStyleSheet("color:#93a4b8;font-size:12px;")
        self.stats_label.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addStretch(1)
        layout.addLayout(header_layout)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.stats_label)

        return card

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    def _create_output_editor(self) -> QPlainTextEdit:
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        font = QFont("Consolas")
        font.setPointSize(11)
        editor.setFont(font)
        return editor

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addToolBar(toolbar)

        generate_action = QAction("Generate", self)
        generate_action.triggered.connect(self.generate_output)

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_output)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_output)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_output)

        toolbar.addAction(generate_action)
        toolbar.addAction(copy_action)
        toolbar.addAction(save_action)
        toolbar.addAction(clear_action)

    def _build_statusbar(self) -> None:
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Ready")

    def browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.path_input.setText(folder)

    def _parse_csv_text(self, value: str) -> set[str]:
        value = value.strip()
        if not value:
            return set()
        return {item.strip() for item in value.split(",") if item.strip()}

    def _parse_max_depth(self) -> int | None:
        value = self.max_depth_input.text().strip()
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
        path_str = self.path_input.text().strip()
        if not path_str:
            QMessageBox.warning(self, "Missing Path", "Please select a project folder.")
            return

        path = Path(path_str)
        if not path.exists() or not path.is_dir():
            QMessageBox.critical(self, "Invalid Path", "The selected path is not a valid directory.")
            return

        try:
            self.statusBar().showMessage("Scanning project...")
            max_depth = self._parse_max_depth()

            config = ScanConfig(
                root_path=path,
                ignored_dirs=self._parse_csv_text(self.ignored_dirs_edit.toPlainText()),
                ignored_files=self._parse_csv_text(self.ignored_files_edit.toPlainText()),
                include_hidden=self.include_hidden_checkbox.isChecked(),
                max_depth=max_depth,
                follow_symlinks=self.follow_symlinks_checkbox.isChecked(),
            )

            tree = scan_project(config)
            self.tree_output = build_tree_text(tree)
            self.json_output = export_json(tree)
            self.combined_output = f"=== TREE ===\n{self.tree_output}\n\n=== JSON ===\n{self.json_output}"

            self.tree_editor.setPlainText(self.tree_output)
            self.json_editor.setPlainText(self.json_output)
            self.combined_editor.setPlainText(self.combined_output)

            stats = calculate_stats(tree)
            stats_text = (
                f"Directories: {stats['directories']} | "
                f"Files: {stats['files']} | "
                f"Total Nodes: {stats['total_nodes']}"
            )
            self.stats_label.setText(stats_text)
            self.statusBar().showMessage("Scan completed successfully.", 4000)

            selected_format = self.format_combo.currentText().strip().lower()
            if selected_format == "tree":
                self.tabs.setCurrentIndex(0)
            elif selected_format == "json":
                self.tabs.setCurrentIndex(1)
            else:
                self.tabs.setCurrentIndex(2)

        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            self.statusBar().showMessage("Error occurred.", 4000)

    def _current_editor(self) -> QPlainTextEdit:
        return self.tabs.currentWidget()

    def copy_output(self) -> None:
        editor = self._current_editor()
        content = editor.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "No Content", "There is no output to copy.")
            return

        QApplication.clipboard().setText(content)
        self.statusBar().showMessage("Output copied to clipboard.", 3000)

    def save_output(self) -> None:
        editor = self._current_editor()
        content = editor.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "No Content", "There is no output to save.")
            return

        current_index = self.tabs.currentIndex()
        default_name = "output.txt"
        if current_index == 1:
            default_name = "output.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Output",
            default_name,
            "Text Files (*.txt);;JSON Files (*.json);;All Files (*.*)",
        )
        if not file_path:
            return

        try:
            Path(file_path).write_text(content, encoding="utf-8")
            self.statusBar().showMessage(f"Saved: {file_path}", 4000)
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", str(exc))

    def clear_output(self) -> None:
        self.tree_editor.clear()
        self.json_editor.clear()
        self.combined_editor.clear()
        self.tree_output = ""
        self.json_output = ""
        self.combined_output = ""
        self.stats_label.setText("Ready")
        self.statusBar().showMessage("Cleared.", 3000)


def run_qt_app() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = ProjectMapMainWindow()
    window.show()
    sys.exit(app.exec())
