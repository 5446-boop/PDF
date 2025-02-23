"""
PDF Highlighter 2.0 - Log Handler
Last Updated: 2025-02-23 11:09:11 UTC
Author: 5446-boop
"""

import logging
import sys
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class QtLogHandler(QObject, logging.Handler):
    """Custom logging handler that emits Qt signals for log messages."""
    new_log_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.setFormatter(
            logging.Formatter(
                '[%(asctime)s UTC][%(levelname)s][%(name)s]: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.setLevel(logging.INFO)

    def emit(self, record):
        """Format and emit a log record."""
        try:
            if self.filter(record):
                msg = self.format(record)
                self.new_log_message.emit(msg)
        except Exception:
            self.handleError(record)