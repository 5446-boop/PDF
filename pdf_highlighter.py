"""
PDF Highlighter 2.0

A PyQt5-based PDF viewer and highlighter application that allows users to:
- Load PDF files
- Search for text
- Add highlights with custom colors
- Remove highlights
- Save modified PDFs

Usage:
    python pdf_highlighter.py

Requirements:
    - PyQt5
    - PyMuPDF (fitz)

Author: 5446-boop
Last Updated: 2025-02-23 01:22:21 UTC
"""

import sys
import traceback
from pathlib import Path

# Add project root to Python path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

def print_error(title, message):
    """Print error to console in an easily readable format."""
    print("\n" + "="*50)
    print(f"ERROR: {title}")
    print("-"*50)
    print(message)
    print("="*50 + "\n")

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
except ImportError as e:
    print_error("Import Error", 
        "PyQt5 is not installed.\n"
        "Please install required packages:\n"
        "pip install -r requirements.txt"
    )
    sys.exit(1)

def show_error(title, message):
    """Show error in both GUI and console."""
    print_error(title, message)
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(title)
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

def main():
    """Main application entry point."""
    try:
        # Initialize Qt Application
        app = QApplication(sys.argv)
        
        # Import MainWindow here to catch import errors
        try:
            from src.ui import MainWindow
        except ImportError as e:
            error_msg = f"Failed to load application: {str(e)}"
            show_error("Import Error", error_msg)
            return 1
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start Qt event loop
        return app.exec_()
        
    except Exception as e:
        error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        show_error("Application Error", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())