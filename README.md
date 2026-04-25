# ProjectMap AI

ProjectMap AI is a simple desktop tool for scanning project directories and exporting a clean folder/file structure that can be shared with AI tools for analysis.

It helps developers quickly generate a readable project map in formats like Tree Text and JSON.

---

## Features

- Select a project folder using a desktop UI
- Scan all folders and files recursively
- Ignore unnecessary folders like `.git`, `node_modules`, `venv`, `__pycache__`
- Export project structure as:
  - Tree Text
  - JSON
  - Both
- Copy output to clipboard
- Save output to file
- Simple, clean, and extendable architecture

---

## Project Structure
```text
projectmap-ai/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── main.py
│
├── src/
│   └── projectmap_ai/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── scanner.py
│       │   ├── tree_builder.py
│       │   ├── json_exporter.py
│       │   └── stats.py
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   └── tkinter_app.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── path_utils.py
│
├── exports/
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   └── test_scanner.py
│
└── docs/
└── usage.md

---

## Requirements

- Python 3.10+
- Tkinter

Usually Tkinter is included with Python.

On Ubuntu/Debian, if Tkinter is missing:

bash
sudo apt install python3-tk

---

## Installation

### 1. Clone the repository

bash
git clone https://github.com/YOUR_USERNAME/projectmap-ai.git
cd projectmap-ai

### 2. Create virtual environment

#### Windows

bash
python -m venv .venv

#### macOS / Linux

bash
python3 -m venv .venv

### 3. Activate virtual environment

#### Windows

bash
.venv\Scripts\activate

#### macOS / Linux

bash
source .venv/bin/activate

### 4. Install dependencies

bash
pip install -r requirements.txt

### 5. Run the application

bash
python main.py

---

## Usage

1. Open the application
2. Click `Browse`
3. Select your project directory
4. Choose output format:
   - Tree Text
   - JSON
   - Both
5. Click `Scan Project`
6. Copy or save the output

---

## Example Tree Output

text
my-project/
├── app/
│   ├── main.py
│   └── routes.py
├── requirements.txt
└── README.md

---

## Example JSON Output

json
{
  "name": "my-project",
  "type": "directory",
  "path": "C:/projects/my-project",
  "children": [
{
"name": "app",
"type": "directory",
"path": "C:/projects/my-project/app",
"children": [
{
"name": "main.py",
"type": "file",
"path": "C:/projects/my-project/app/main.py"
}
]
}
  ]
}

---

## Ignore Defaults

The application ignores these folders by default:

text
.git
.idea
.vscode
__pycache__
node_modules
venv
.venv
dist
build
.next
.nuxt
coverage

And these files:

text
.DS_Store
Thumbs.db

---

## Roadmap

Planned features:

- Markdown export
- AI-ready prompt generation
- File size display
- File extension statistics
- Maximum scan depth
- Include/exclude patterns
- Dark mode UI
- Export to `.md`, `.json`, `.txt`
- Optional preview of important files
- Packaging as executable file for Windows/macOS/Linux

---

## License

MIT License


---

# 11. فایل `main.py`

```python
from projectmap_ai.app import run_app


if __name__ == "__main__":
    run_app()
