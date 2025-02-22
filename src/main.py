#!/usr/bin/env python3
"""
PDF Highlighter 2.0 main entry point
Last Updated: 2025-02-22
"""

import sys
import logging
from pathlib import Path
from PyQt5 import QtWidgets

from .ui import MainWindow
from .config import AppConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(AppConfig.LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Set application metadata
        app.setApplicationName(AppConfig.APP_NAME)
        app.setApplicationVersion(AppConfig.VERSION)
        app.setOrganizationName(AppConfig.ORGANIZATION)
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application error: {e}")
        QtWidgets.QMessageBox.critical(None, "Error", f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()