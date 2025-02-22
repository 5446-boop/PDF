"""
PDF Highlighter 2.0 - Main Entry Point
Last Updated: 2025-02-22 20:48:47 UTC
Version: 2.0.0
"""

import sys
import logging
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui import MainWindow
from src.config.settings import AppConfig

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format=AppConfig.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(AppConfig.LOG_FILE)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def main():
    """Main application entry point."""
    try:
        from PyQt5 import QtWidgets
        
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Set application metadata
        app.setApplicationName(AppConfig.APP_NAME)
        app.setApplicationVersion(AppConfig.VERSION)
        app.setOrganizationName(AppConfig.ORGANIZATION)
        
        window = MainWindow()
        window.setMinimumSize(AppConfig.MIN_WINDOW_WIDTH, AppConfig.MIN_WINDOW_HEIGHT)
        window.resize(AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Application error: {e}")
        QtWidgets.QMessageBox.critical(None, "Error", f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()