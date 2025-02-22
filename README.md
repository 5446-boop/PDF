# PDF Highlighter

A Python application for highlighting and managing text in PDF files. The application allows you to search for specific material numbers in PDF documents and highlight them with custom colors.

## Features
- Search for text in multiple PDF files
- Highlight text with custom colors
- Sound notifications for matches
- Interactive GUI interface
- Track highlighted entries in a table view

## Requirements
- Python 3.6+
- PyMuPDF (fitz)
- Pygame
- Tkinter (usually comes with Python)

## Installation
1. Clone the repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the application:
```bash
python -m pdf_highlighter
```

## Project Structure
```
pdf_highlighter/
├── pdf_highlighter/
│   ├── __init__.py
│   ├── app.py            # Main application class
│   ├── utils.py          # Utility functions
│   └── gui/
│       ├── __init__.py
│       └── components.py  # GUI components
├── tests/
│   ├── __init__.py
│   ├── test_utils.py
│   └── test_app.py
├── resources/
│   ├── match_found_soft.wav
│   └── no_match_soft.wav
├── requirements.txt
├── setup.py
└── README.md
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.