"""
PDF Highlighter 2.0 - Main Application Module
Last Updated: 2025-02-22 21:17:16 UTC
"""

import sys
import logging
from pathlib import Path

from src.ui.qt_imports import QApplication, Qt
from src.ui.main_window import MainWindow
from src.config.settings import AppConfig

logger = logging.getLogger(__name__)

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

def main():
    """Main application entry point."""
    logger = setup_logging()
    
    try:
        if not QApplication.instance():
            app = QApplication(sys.argv)
            app.setStyle('Fusion')
        
        window = MainWindow()
        window.show()
        
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())