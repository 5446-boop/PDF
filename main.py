#!/usr/bin/env python3
"""
PDF Highlighter 2.0
A PyQt5-based PDF viewer and highlighter application.
"""

import sys
import logging
from pathlib import Path
from PyQt5 import QtWidgets
from ui import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pdf_highlighter.log')
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Verify all required dependencies are available."""
    try:
        import fitz
        import PyQt5
        logger.info("All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        QtWidgets.QMessageBox.critical(
            None,
            "Error",
            f"Missing required dependency: {e}\nPlease install all requirements: pip install -r requirements.txt"
        )
        return False

def main():
    """Main application entry point."""
    if not check_dependencies():
        sys.exit(1)

    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')  # Modern look across platforms
        
        # Set application metadata
        app.setApplicationName("PDF Highlighter")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("5446-boop")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application error: {e}")
        QtWidgets.QMessageBox.critical(None, "Error", f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()