"""
PDF Highlighter 2.0 - Search Handler
Last Updated: 2025-02-23 11:38:03 UTC
Author: 5446-boop
"""

import logging
import traceback
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)

class SearchHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        
    def search_text(self):
        """Handle text search."""
        text = self.main_window.search_input.text().strip()
        if not text:
            self.main_window.show_error("Search Error", "Please enter search text")
            return
            
        logger.info(f"Searching for: '{text}'")
        try:
            results = self.main_window.pdf_handler.search_text(text)
            self.main_window.results_table.setRowCount(0)
            
            for result in results:
                row = self.main_window.results_table.rowCount()
                self.main_window.results_table.insertRow(row)
                self.add_result_to_table(row, result)
                
            if not results:
                logger.info(f"No matches found for '{text}'")
                self.main_window.show_error("Search Results", f"No matches found for '{text}'")
                
        except Exception as e:
            self.main_window.show_error("Search Error", str(e))
            logger.error(f"Search error: {traceback.format_exc()}")

    def add_result_to_table(self, row, result):
        """Add a search result to the table."""
        try:
            # Page number
            page_item = QTableWidgetItem(str(result.page_num))
            page_item.setData(Qt.UserRole, result.rects)
            page_item.setFlags(page_item.flags() & ~Qt.ItemIsEditable)
            self.main_window.results_table.setItem(row, 0, page_item)
            
            # Found count
            found_count = len(result.rects)
            found_item = QTableWidgetItem(str(found_count))
            found_item.setFlags(found_item.flags() & ~Qt.ItemIsEditable)
            self.main_window.results_table.setItem(row, 1, found_item)
            
            # Color status
            color_item = QTableWidgetItem()
            color_item.setFlags(Qt.ItemIsEnabled)
            self.main_window.results_table.update_highlight_status(
                color_item,
                result.highlight_color is not None,
                result.highlight_color
            )
            if result.annot_xrefs:
                color_item.setData(Qt.UserRole, result.annot_xrefs)
            self.main_window.results_table.setItem(row, 2, color_item)
            
            # Buttons
            highlight_btn = self.main_window.results_table.create_action_button("Highlight All")
            highlight_btn.clicked.connect(
                lambda: self.main_window.highlight_handler.add_highlight(row, result.text)
            )
            self.main_window.results_table.setCellWidget(row, 3, highlight_btn)
            
            remove_btn = self.main_window.results_table.create_action_button("Remove All")
            remove_btn.clicked.connect(
                lambda: self.main_window.highlight_handler.remove_highlight(row)
            )
            self.main_window.results_table.setCellWidget(row, 4, remove_btn)
            
            logger.debug(f"Added result for page {result.page_num} with {found_count} matches")
            
        except Exception as e:
            logger.error(f"Error adding result to table: {traceback.format_exc()}")

    def refresh_search_results(self):
        """Refresh the search results to show current highlight status."""
        current_text = self.main_window.search_input.text().strip()
        if current_text:
            logger.debug("Refreshing search results")
            self.search_text()