"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-23 11:05:10 UTC
Author: 5446-boop
"""

import sys
import logging
import traceback
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QTextEdit, QFileDialog, QSplitter,
    QMessageBox, QTableWidgetItem,
    QMenuBar, QMenu, QAction,
    QCheckBox
)
from PyQt5.QtCore import Qt
from src.utils.log_handler import QtLogHandler

from .base_window import BaseWindow
from .widgets.color_picker import ColorPicker
from .widgets.results_table import ResultsTable
from .widgets.about_dialog import AboutDialog
from src.utils.pdf_handler import PDFHandler, PDFError

logger = logging.getLogger(__name__)

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        try:
            # Initialize logging
            self.setup_logging()
            
            self.pdf_handler = PDFHandler()
            self.setup_ui()
            logger.info("Application started")
        except Exception as e:
            error_msg = f"Error initializing MainWindow: {str(e)}\n\n{traceback.format_exc()}"
            logger.error(error_msg)
            print("\nERROR:", error_msg)
            raise

    def toggle_debug(self, state):
        """Toggle debug logging for the program output."""
        if state == Qt.Checked:
            self.qt_log_handler.setLevel(logging.DEBUG)
            # Use root logger to ensure all modules get the message
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            # Log using debug level
            logging.getLogger(__name__).debug("Debug logging enabled")
            
            # Ensure pdf_handler logger is at debug level
            pdf_logger = logging.getLogger('src.utils.pdf_handler')
            pdf_logger.setLevel(logging.DEBUG)
        else:
            self.qt_log_handler.setLevel(logging.INFO)
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            logging.getLogger(__name__).info("Debug logging disabled")

    def setup_logging(self):
        """Setup logging configuration."""
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create console handler
        console_format = logging.Formatter(
            '[%(asctime)s UTC][%(levelname)s][%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        # Create Qt handler for program output
        self.qt_log_handler = QtLogHandler()
        self.qt_log_handler.setLevel(logging.INFO)  # Start with INFO level
        self.qt_log_handler.new_log_message.connect(self.append_log_message)
        root_logger.addHandler(self.qt_log_handler)
        
        # Explicitly set DEBUG level for all relevant loggers
        loggers = ['src.utils.pdf_handler', 'src.ui.main_window']
        for name in loggers:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            logger.propagate = True

    def log_message(self, message):
        """Log a message at INFO level."""
        logger = logging.getLogger(__name__)
        logger.info(message)

    def append_log_message(self, message):
        """Append a message to the log output."""
        self.log_output.append(message)
        # Auto-scroll to the bottom
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Highlighter")
        self.setMinimumSize(1000, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create splitter for main layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Create left panel (controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File selection
        file_group = QWidget()
        file_layout = QHBoxLayout(file_group)
        self.select_btn = QPushButton("Select PDF")
        self.select_btn.clicked.connect(self.select_pdf)
        file_layout.addWidget(self.select_btn)
        
        self.path_label = QLabel("No file selected")
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label)
        left_layout.addWidget(file_group)
        
        # Search
        search_group = QWidget()
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        search_layout.addWidget(self.search_input)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_text)
        search_layout.addWidget(self.search_btn)
        left_layout.addWidget(search_group)
        
        # Color picker
        self.color_picker = ColorPicker()
        left_layout.addWidget(self.color_picker)
        
        left_layout.addStretch()
        
        # Create right panel (log)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Debug checkbox
        debug_layout = QHBoxLayout()
        self.debug_checkbox = QCheckBox("Enable Debug Logging")
        self.debug_checkbox.stateChanged.connect(self.toggle_debug)
        debug_layout.addWidget(self.debug_checkbox)
        debug_layout.addStretch()
        right_layout.addLayout(debug_layout)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        right_layout.addWidget(self.log_output)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create results table
        self.results_table = ResultsTable()
        main_layout.addWidget(self.results_table)

    def create_menu_bar(self):
        """Create the menu bar with File and About options."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # About Menu (right-aligned)
        about_menu = QMenu('Settings', self)
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about_dialog)
        about_menu.addAction(about_action)
        
        # Add About menu to the right side of the menu bar
        menubar.addMenu(about_menu)

    def show_about_dialog(self):
        """Show the About dialog."""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def toggle_debug(self, state):
        """Toggle debug logging."""
        if state == Qt.Checked:
            logger.setLevel(logging.DEBUG)
            self.log_message("Debug logging enabled")
        else:
            logger.setLevel(logging.INFO)
            self.log_message("Debug logging disabled")

    def select_pdf(self):
        """Handle PDF file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        
        if file_path:
            try:
                if self.pdf_handler.load_document(file_path):
                    self.path_label.setText(file_path)
                    self.log_message(f"Loaded PDF: {file_path}")
                    self.results_table.setRowCount(0)
            except PDFError as e:
                self.show_error("PDF Error", str(e))
                self.log_message(f"Error loading PDF: {e}")
            except Exception as e:
                self.show_error("Error", f"Unexpected error: {str(e)}")
                self.log_message(f"Unexpected error: {e}")

    def search_text(self):
        """Handle text search."""
        text = self.search_input.text().strip()
        if not text:
            self.show_error("Search Error", "Please enter search text")
            return
            
        self.log_message(f"Searching for: {text}")
        try:
            results = self.pdf_handler.search_text(text)
            self.results_table.setRowCount(0)
            
            for result in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.add_result_to_table(row, result)
                
            if not results:
                self.show_error("Search Results", f"No matches found for '{text}'")
                
        except Exception as e:
            self.show_error("Search Error", str(e))
            logger.error(f"Search error: {traceback.format_exc()}")

    def add_result_to_table(self, row, result):
        """Add a search result to the table."""
        try:
            # Page number
            page_item = QTableWidgetItem(str(result.page_num))
            page_item.setData(Qt.UserRole, result.rects)
            page_item.setFlags(page_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 0, page_item)
            
            # Found count
            found_count = len(result.rects)
            found_item = QTableWidgetItem(str(found_count))
            found_item.setFlags(found_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 1, found_item)
            
            # Color status
            color_item = QTableWidgetItem()
            color_item.setFlags(Qt.ItemIsEnabled)
            self.results_table.update_highlight_status(
                color_item,
                result.highlight_color is not None,
                result.highlight_color
            )
            if result.annot_xrefs:
                color_item.setData(Qt.UserRole, result.annot_xrefs)
            self.results_table.setItem(row, 2, color_item)
            
            # Buttons
            highlight_btn = self.results_table.create_action_button("Highlight All")
            highlight_btn.clicked.connect(lambda: self.add_highlight(row, result.text))
            self.results_table.setCellWidget(row, 3, highlight_btn)
            
            remove_btn = self.results_table.create_action_button("Remove All")
            remove_btn.clicked.connect(lambda: self.remove_highlight(row))
            self.results_table.setCellWidget(row, 4, remove_btn)
            
        except Exception as e:
            self.log_message(f"Error adding result to table: {e}")
            logger.error(f"Error adding result to table: {traceback.format_exc()}")

    def add_highlight(self, row, text):
        """Add highlights to all instances of text on the specified page."""
        try:
            page_item = self.results_table.item(row, 0)
            color_item = self.results_table.item(row, 2)  # Updated from 1 to 2
            
            if not page_item or not color_item:
                return
                
            page_num = int(page_item.text())  # No need to split now
            rects = page_item.data(Qt.UserRole)
            
            if not color_item.data(Qt.UserRole + 1):
                xrefs = self.pdf_handler.highlight_text(page_num, rects, self.color_picker.get_color(), text)
                if xrefs:
                    self.results_table.update_highlight_status(color_item, True, self.color_picker.get_color())
                    color_item.setData(Qt.UserRole, xrefs)
                    self.log_message(f"Added {len(rects)} highlights on page {page_num}")
                    # Refresh the search results to show updated highlight status
                    self.refresh_search_results()
                    
        except Exception as e:
            self.log_message(f"Error adding highlights: {e}")
            logger.error(f"Error adding highlights: {traceback.format_exc()}")

    def remove_highlight(self, row):
        """Remove all highlights from the specified page."""
        try:
            page_item = self.results_table.item(row, 0)
            color_item = self.results_table.item(row, 2)  # Updated from 1 to 2
            
            if not page_item or not color_item:
                return
                
            page_num = int(page_item.text())  # No need to split now
            xrefs = color_item.data(Qt.UserRole)
            
            if xrefs and color_item.data(Qt.UserRole + 1):
                if self.pdf_handler.remove_highlight(page_num, xrefs):
                    self.results_table.update_highlight_status(color_item, False)
                    color_item.setData(Qt.UserRole, None)
                    self.log_message(f"Removed all highlights on page {page_num}")
                    # Refresh the search results to show updated highlight status
                    self.refresh_search_results()
                    
        except Exception as e:
            self.log_message(f"Error removing highlights: {e}")
            logger.error(f"Error removing highlights: {traceback.format_exc()}")

    def refresh_search_results(self):
        """Refresh the search results to show current highlight status."""
        current_text = self.search_input.text().strip()
        if current_text:
            self.search_text()

    def save_pdf(self):
        """Save PDF with highlights."""
        if not self.pdf_handler.filepath:
            self.show_error("Save Error", "No PDF file loaded")
            return
        
        reply = QMessageBox.question(
            self,
            'Save PDF',
            'Do you want to overwrite the existing file?',
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Reload the document before saving to ensure all changes are captured
                if self.pdf_handler.reload_document():
                    if self.pdf_handler.save_document(self.pdf_handler.filepath):
                        self.log_message(f"Saved PDF with highlights to: {self.pdf_handler.filepath}")
                    else:
                        raise PDFError("Failed to save PDF")
                else:
                    raise PDFError("Failed to reload PDF before saving")
            except Exception as e:
                self.show_error("Save Error", str(e))
                self.log_message(f"Error saving PDF: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            if self.pdf_handler:
                self.pdf_handler.close()
        except:
            pass
        super().closeEvent(event)