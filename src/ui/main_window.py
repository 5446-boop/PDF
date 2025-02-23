"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-23 02:58:24 UTC
Author: 5446-boop
"""

import logging
import traceback
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QTextEdit, QFileDialog, QSplitter,
    QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import Qt

from .base_window import BaseWindow
from .widgets.color_picker import ColorPicker
from .widgets.results_table import ResultsTable
from src.utils.pdf_handler import PDFHandler, PDFError

logger = logging.getLogger(__name__)

class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__()
        try:
            self.pdf_handler = PDFHandler()
            self.setup_ui()
            self.log_message("Application started")
        except Exception as e:
            error_msg = f"Error initializing MainWindow: {str(e)}\n\n{traceback.format_exc()}"
            logger.error(error_msg)
            print("\nERROR:", error_msg)
            raise

    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Highlighter")
        self.setMinimumSize(1000, 800)
        
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
        
        # Save button
        self.save_btn = QPushButton("Save PDF")
        self.save_btn.clicked.connect(self.save_pdf)
        left_layout.addWidget(self.save_btn)
        
        left_layout.addStretch()
        
        # Create right panel (log)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.log_output)
        
        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create results table
        self.results_table = ResultsTable()
        main_layout.addWidget(self.results_table)

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