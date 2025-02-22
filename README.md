# PDF Highlighter 2.0

A PyQt5-based PDF viewer and highlighter application that allows you to search, highlight, and manage annotations in PDF documents.

## Features

- 📄 Open and view PDF documents
- 🔍 Search for text within PDF files
- 🖍️ Highlight text with customizable colors
- 📑 Toggle highlights on/off
- 🎯 Navigate through pages easily
- 📊 View search results in a table
- 📝 Track changes with integrated logging

## Installation

```bash
# Install from PyPI
pip install pdf-highlighter

# Install from source
git clone https://github.com/5446-boop/PDF.git
cd PDF
pip install -e .
```

## Usage

```bash
# Start the application
pdf-highlighter

# Or run from source
python -m pdf_highlighter
```

## Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src

# Lint code
flake8 src tests
```

## Project Structure

```
PDF/
├── src/
│   └── pdf_highlighter/
│       ├── __init__.py
│       ├── main.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── viewer.py
│       │   ├── main_window.py
│       │   └── shortcuts.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── pdf_utils.py
│       │   └── pdf_processor.py
│       └── config/
│           ├── __init__.py
│           └── settings.py
├── tests/
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.7+
- PyQt5 5.15+
- PyMuPDF 1.19+

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Version History

### 2.0.0 (2025-02-22)
- Reorganized project structure
- Added proper logging
- Improved error handling
- Enhanced UI with modern style
- Added keyboard shortcuts
- Added configuration management

### 1.0.0
- Initial release
- Basic PDF viewing and highlighting functionality