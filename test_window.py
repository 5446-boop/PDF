"""
PDF Highlighter 2.0 - Test Script
Last Updated: 2025-02-22 21:19:08 UTC
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def test_window():
    """Test the main window."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_window())