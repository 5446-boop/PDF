"""
PDF Highlighter 2.0 - Keyboard Shortcuts
Last Updated: 2025-02-22 20:41:04 UTC
Version: 2.0.0
"""

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

class Shortcuts:
    """Manages application keyboard shortcuts."""
    
    def __init__(self, window):
        """Initialize shortcuts for the main window."""
        self.window = window
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup all keyboard shortcuts."""
        # File operations
        QShortcut(QKeySequence.Open, self.window, self.window.open_pdf)
        QShortcut(QKeySequence.Save, self.window, self.window.save_highlights)
        QShortcut(QKeySequence.Quit, self.window, self.window.close)
        
        # Navigation
        QShortcut(QKeySequence.ZoomIn, self.window, self.window.viewer.zoom_in)
        QShortcut(QKeySequence.ZoomOut, self.window, self.window.viewer.zoom_out)
        
        next_page = QShortcut(QKeySequence("PgDown"), self.window)
        next_page.activated.connect(self.window.viewer.next_page)
        
        prev_page = QShortcut(QKeySequence("PgUp"), self.window)
        prev_page.activated.connect(self.window.viewer.previous_page)
        
        # Custom shortcuts
        QShortcut(QKeySequence("Ctrl+H"), self.window, self.window.choose_color)
        QShortcut(QKeySequence("Ctrl+F"), self.window, self.window.viewer.toggle_fullscreen)