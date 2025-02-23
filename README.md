# PDF Highlighter

A PyQt5-based PDF viewer and highlighter that allows searching and highlighting text in PDF documents.

## Features
- Load and view PDF files
- Search for text within PDFs
- Highlight text with custom colors
- Remove highlights with double-click
- Save PDFs with highlights
- Log window for operation tracking

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

## Usage

1. Run the application:
```bash
python pdf_highlighter.py
```

2. Use the interface to:
   - Select a PDF file
   - Search for text
   - Choose highlight colors
   - Double-click results to toggle highlights
   - Save the modified PDF

## Requirements
- Python 3.7+
- PyQt5
- PyMuPDF (fitz)

## Project Structure
```
PDF/
├── README.md           # Project documentation
├── requirements.txt    # Package dependencies
├── pdf_highlighter.py  # Main entry point
└── src/               # Source code
    ├── ui/           # User interface components
    └── utils/        # Utility functions and classes
```

## Development
- Last Updated: 2025-02-23 01:22:21 UTC
- Author: 5446-boop

## License
MIT License