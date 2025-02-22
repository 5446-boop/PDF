"""
Keyboard shortcuts configuration.
"""
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

class Shortcuts:
    """Manages application keyboard shortcuts."""
    
    def __init__(self, window):
        self.window = window
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup all keyboard shortcuts."""
        # Navigation
        QShortcut(QKeySequence.ZoomIn, self.window, self.window.viewer.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self.window.viewer.zoom_out)
        
        # Page navigation
        next_page = QShortcut(QKeySequence("PgDown"), self.window)
        next_page.activated.connect(self.window.viewer.next_page)
        
        prev_page = QShortcut(QKeySequence("PgUp"), self.window)
        prev_page.activated.connect(self.window.viewer.previous_page)
        
        # File operations
        open_file = QShortcut(QKeySequence.Open, self.window)
        open_file.activated.connect(self.window.open_pdf)