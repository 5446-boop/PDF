"""
PDF Highlighter 2.0 - Color Picker Widget
Last Updated: 2025-02-23 02:09:55 UTC
Author: 5446-boop
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QColorDialog
from PyQt5.QtGui import QColor

class ColorPicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_color = (1, 1, 0)  # Default yellow
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        self.color_btn = QPushButton("Select Color")
        self.color_btn.clicked.connect(self.select_color)
        layout.addWidget(self.color_btn)
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self.update_color_preview()
        layout.addWidget(self.color_preview)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = (
                color.red() / 255.0,
                color.green() / 255.0,
                color.blue() / 255.0
            )
            self.update_color_preview()
            return True
        return False

    def update_color_preview(self):
        r, g, b = self.current_color
        style = (f"background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)}); "
                f"border: 1px solid black;")
        self.color_preview.setStyleSheet(style)

    def get_color(self):
        return self.current_color