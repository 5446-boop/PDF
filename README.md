# PDF Highlighter 2.0

A powerful PyQt5-based PDF viewer and highlighter application that allows searching, highlighting, and managing text in PDF documents with an intuitive interface.

## Features
- 📄 Load and view PDF files seamlessly
- 🔍 Advanced text search capabilities
- 🎨 Customizable highlight colors
- ⚡ Quick highlight removal with double-click
- 💾 Save PDFs with highlights preserved
- 📊 Detailed logging and debug options
- 🎯 Results table with page numbers and counts
- ⌨️ Keyboard shortcuts for common actions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/5446-boop/PDF.git
cd PDF
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/ui/main_window.py
```

## Interface Guide
- **File Selection**: Use "Select PDF" button or Alt+S
- **Search**: 
  - Enter search text
  - Click "Search" or use Alt+F
  - Results show page numbers and match counts
- **Highlighting**:
  - Choose colors from the color picker
  - Click "Highlight All" on results
  - Double-click to remove highlights
  - Use "Remove All" to clear highlights
- **Logging**:
  - Toggle debug mode for detailed logs
  - Clear logs with "Clear Log" button
  - Real-time operation tracking

## Requirements
- Python 3.7+
- PyQt5 5.15+
- PyMuPDF (fitz) 1.19+
- pywin32 (Windows only)

## Project Structure
```
PDF/
├── README.md           # Project documentation
├── requirements.txt    # Package dependencies
└── src/               # Source code
    ├── ui/            # User interface components
    │   ├── widgets/   # Custom UI widgets
    │   ├── main_window.py
    │   └── ui_components.py
    └── utils/         # Utility modules
        ├── log_handler.py
        └── pdf_handler.py
```

## Development
- Version: 2.0
- Last Updated: 2025-02-23 12:34:41 UTC
- Author: 5446-boop
- Language: Python (100%)

## License
MIT License - See LICENSE file for details.

## Contact
- GitHub: [@5446-boop](https://github.com/5446-boop)
- Project Link: [https://github.com/5446-boop/PDF](https://github.com/5446-boop/PDF)