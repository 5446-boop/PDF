"""
PDF Highlighter 2.0 - Highlight Handler
Last Updated: 2025-02-24 18:22:24 UTC
Author: 5446-boop
"""

import logging
import traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from ..utils.pdf_handler import PDFError

logger = logging.getLogger(__name__)

class HighlightHandler:
    def __init__(self, main_window):
        self.main_window = main_window

    def add_highlight(self, row, text):
        """Add highlights to all instances of text on the specified page."""
        try:
            page_item = self.main_window.results_table.item(row, 0)
            color_item = self.main_window.results_table.item(row, 4)
            
            if not page_item or not color_item:
                logger.warning(f"Missing items - page_item: {bool(page_item)}, color_item: {bool(color_item)}")
                return
                
            page_num = int(page_item.text().split('/')[0])
            bboxes = page_item.data(Qt.UserRole)
            
            if not color_item.data(Qt.UserRole + 1):  # If not already highlighted
                logger.debug(f"Adding highlights on page {page_num} for '{text}'")
                xrefs = self.main_window.pdf_handler.highlight_text(
                    page_num, 
                    bboxes, 
                    self.main_window.color_picker.get_color(), 
                    text
                )
                if xrefs:
                    self.main_window.results_table.update_highlight_status(
                        color_item, 
                        True, 
                        self.main_window.color_picker.get_color()
                    )
                    self.main_window.search_handler.refresh_search_results()
                    
        except Exception as e:
            logger.error(f"Error adding highlights: {traceback.format_exc()}")

    def remove_highlight(self, row):
        """Remove all highlights from the specified page."""
        try:
            logger.debug(f"Attempting to remove highlights for row {row}")
            
            page_item = self.main_window.results_table.item(row, 0)
            color_item = self.main_window.results_table.item(row, 4)
            
            if not page_item or not color_item:
                logger.warning(f"Missing items - page_item: {bool(page_item)}, color_item: {bool(color_item)}")
                return
            
            # Get the page number and search text
            page_num = int(page_item.text().split('/')[0])
            text = self.main_window.search_input.text().strip()
            
            logger.debug(f"Removing highlights for text '{text}' on page {page_num}")
            if self.main_window.pdf_handler.remove_highlight_by_text(page_num, text):
                self.main_window.results_table.update_highlight_status(color_item, False)
                logger.info(f"Successfully removed highlights from page {page_num}")
                self.main_window.search_handler.refresh_search_results()
            else:
                logger.warning(f"Failed to remove highlights from page {page_num}")
                
        except Exception as e:
            logger.error(f"Error removing highlights: {traceback.format_exc()}")

    def save_pdf(self):
        """Save PDF with highlights."""
        if not self.main_window.pdf_handler.filepath:
            self.main_window.show_error("Save Error", "No PDF file loaded")
            return
        
        reply = QMessageBox.question(
            self.main_window,
            'Save PDF',
            'Do you want to overwrite the existing file?',
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Yes:
            try:
                logger.debug("Saving PDF with highlights")
                if self.main_window.pdf_handler.save():
                    logger.info(f"Successfully saved PDF to: {self.main_window.pdf_handler.filepath}")
                else:
                    raise PDFError("Failed to save PDF")
            except Exception as e:
                self.main_window.show_error("Save Error", str(e))
                logger.error(f"Error saving PDF: {e}")