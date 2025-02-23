"""
PDF Highlighter 2.0 - About Dialog
Last Updated: 2025-02-23 10:48:15 UTC
Author: 5446-boop
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the About dialog UI."""
        self.setWindowTitle("About PDF Highlighter")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Application name
        app_name = QLabel("PDF Highlighter 2.0")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(app_name)
        
        # Version
        version = QLabel("Version: 2.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Author
        author = QLabel("Author: 5446-boop")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)
        
        # Description
        description = QLabel(
            "A powerful PDF highlighting tool that allows you to search, "
            "highlight, and manage annotations in PDF documents."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)