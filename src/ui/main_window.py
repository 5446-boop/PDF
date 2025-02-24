"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-23 11:38:03 UTC
Author: 5446-boop
"""

import sys
import logging
import traceback
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QTextEdit, QFileDialog, QSplitter,
    QMessageBox, QMenuBar, QMenu, QAction,
    QCheckBox
)
from PyQt5.QtCore import Qt

from ..utils.log_handler import QtLogHandler
from ..utils.pdf_handler import PDFHandler, PDFError

from .base_window import BaseWindow
from .widgets.about_dialog import AboutDialog
from .ui_components import setup_ui_components
from .search_handler import SearchHandler
from .highlight_handler import HighlightHandler

logger = logging.getLogger(__name__)

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setup_logging()
            self.pdf_handler = PDFHandler(None)  # Initialize with None or a dummy value
            self.search_handler = SearchHandler(self)
            self.highlight_handler = HighlightHandler(self)
            self.setup_ui()
            logger.info("Application started")
        except Exception as e:
            error_msg = f"Error initializing MainWindow: {str(e)}\n\n{traceback.format_exc()}"
            logger.error(error_msg)
            print("\nERROR:", error_msg)
            raise

    def setup_logging(self):
        """Setup logging configuration."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        console_format = logging.Formatter(
            '[%(asctime)s UTC][%(levelname)s][%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        self.qt_log_handler = QtLogHandler()
        self.qt_log_handler.setLevel(logging.INFO)
        self.qt_log_handler.new_log_message.connect(self.append_log_message)
        root_logger.addHandler(self.qt_log_handler)
        
        loggers = ['src.utils.pdf_handler', 'src.ui.main_window']
        for name in loggers:
            module_logger = logging.getLogger(name)
            module_logger.setLevel(logging.DEBUG)
            module_logger.propagate = True

    def clear_log(self):
        """Clear the log output window."""
        self.log_output.clear()
        logger.info("Log cleared")
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Highlighter")
        self.setMinimumSize(1000, 800)
        setup_ui_components(self)

    def toggle_debug(self, state):
        """Toggle debug logging for the program output."""
        if state == Qt.Checked:
            self.qt_log_handler.setLevel(logging.DEBUG)
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            pdf_logger = logging.getLogger('src.utils.pdf_handler')
            pdf_logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        else:
            self.qt_log_handler.setLevel(logging.INFO)
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            logger.info("Debug logging disabled")

    def append_log_message(self, message):
        """Append a message to the log output."""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def show_about_dialog(self):
        """Show the About dialog."""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def select_pdf(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        try:
            logger.debug(f"Attempting to load PDF: {file_path}")
            self.pdf_handler = PDFHandler(file_path)  # Initialize PDFHandler with the file path
            if self.pdf_handler.load_document(file_path):
                logger.debug(f"Successfully loaded PDF with {len(self.pdf_handler.doc)} pages")
                self.path_label.setText(file_path)
                logger.info(f"Loaded PDF: {file_path}")
            else:
                raise PDFError("Failed to load PDF")
        except Exception as e:
            error_msg = f"Error loading PDF: {str(e)}"
            self.show_error("Load Error", error_msg)
            logger.error(error_msg)

    def show_error(self, title, message):
        """Show an error message."""
        QMessageBox.critical(self, title, message)