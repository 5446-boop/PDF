"""
PDF Highlighter 2.0 - Main Module
Last Updated: 2025-02-23 00:45:20 UTC
"""

import sys
from src.ui.qt_imports import QApplication
from src.ui.main_window import MainWindow

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())