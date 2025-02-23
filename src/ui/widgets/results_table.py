"""
PDF Highlighter 2.0 - Results Table Widget
Last Updated: 2025-02-23 10:38:17 UTC
Author: 5446-boop
"""

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

class ResultsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the table UI."""
        self.setColumnCount(5)  # Changed from 4 to 5
        self.setHorizontalHeaderLabels(["Page", "Found", "Color", "Highlight All", "Remove All"])
        
        # Set column widths
        self.setColumnWidth(0, 80)   # Page
        self.setColumnWidth(1, 80)   # Found
        self.setColumnWidth(2, 100)  # Color
        self.setColumnWidth(3, 100)  # Highlight All
        self.setColumnWidth(4, 100)  # Remove All
        
        self.setSortingEnabled(True)

    def create_action_button(self, text):
        """Create a button for the table."""
        button = QPushButton(text)
        button.setFixedWidth(90)
        return button

    def update_highlight_status(self, item, is_highlighted, color=None):
        """Update the color cell with color visualization."""
        if is_highlighted and color:
            hex_color = self.rgb_to_hex(color)
            item.setBackground(QBrush(QColor(hex_color)))
            item.setText("")
            item.setData(Qt.UserRole + 1, color)
        else:
            item.setBackground(QBrush())
            item.setText("")
            item.setData(Qt.UserRole + 1, None)
        item.setFlags(Qt.ItemIsEnabled)

    @staticmethod
    def rgb_to_hex(rgb_tuple):
        """Convert RGB tuple (0-1 range) to hex color string."""
        r, g, b = rgb_tuple
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"