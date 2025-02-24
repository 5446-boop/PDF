"""
PDF Highlighter 2.0 - Results Table Widget
Last Updated: 2025-02-24 17:55:36 UTC
"""

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import logging

logger = logging.getLogger(__name__)

class ResultsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()

    def setup_table(self):
        """Initialize the table with the required columns."""
        # Define columns
        columns = [
            "Page",          # Format: "001/100"
            "Matches",       # Total matches on page
            "Dev. No.",     # Delivery Number
            "Fak. No.",     # Invoice Number
            "Color",        # Highlight color
            "",            # Highlight button column
            ""             # Remove button column
        ]
        
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Set column properties
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Page
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Matches
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)          # Dev. No.
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)          # Fak. No.
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Color
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Highlight
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Remove
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)

    def create_action_button(self, text: str) -> QPushButton:
        """Create a button for the action columns."""
        button = QPushButton(text)
        button.setFixedWidth(80)
        return button

    def update_highlight_status(self, item: QTableWidgetItem, is_highlighted: bool, color: tuple = None):
        """Update the highlight status cell."""
        if is_highlighted and color:
            item.setBackground(QColor.fromRgbF(*color))
            item.setText("✓")
        else:
            item.setBackground(QColor(255, 255, 255))
            item.setText("")
        
        item.setData(Qt.UserRole + 1, is_highlighted)
        item.setTextAlignment(Qt.AlignCenter)