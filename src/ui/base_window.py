"""
PDF Highlighter 2.0 - Base Window Component
Last Updated: 2025-02-23 02:09:55 UTC
Author: 5446-boop
"""

import logging
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseWindow(QMainWindow):
    def show_error(self, title, message):
        """Show error in both GUI and console."""
        print("\n" + "="*50)
        print(f"ERROR: {title}")
        print("-"*50)
        print(message)
        print("="*50 + "\n")
        QMessageBox.critical(self, title, message)

    def log_message(self, message: str):
        """Add message to log output and print to console."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        if hasattr(self, 'log_output'):
            self.log_output.append(log_msg)
        print(log_msg)