"""
PDF Highlighter 2.0 - Keyboard Shortcuts
Defines keyboard shortcuts for the application.
"""

from PyQt5.QtCore import Qt

class Shortcuts:
    """Application keyboard shortcuts."""
    
    # File operations
    OPEN_FILE = "Ctrl+O"
    SAVE_FILE = "Ctrl+S"
    PRINT = "Ctrl+P"
    QUIT = "Ctrl+Q"
    
    # Navigation
    NEXT_PAGE = "Right"
    PREV_PAGE = "Left"
    FIRST_PAGE = "Home"
    LAST_PAGE = "End"
    
    # View
    ZOOM_IN = "Ctrl++"
    ZOOM_OUT = "Ctrl+-"
    FIT_WIDTH = "Ctrl+W"
    FIT_PAGE = "Ctrl+F"
    
    # Search and highlight
    FIND = "Ctrl+F"
    CLEAR_HIGHLIGHTS = "Ctrl+H"
    TOGGLE_HIGHLIGHT = "Ctrl+Space"
    
    @classmethod
    def get_all(cls):
        """Get all shortcuts as a dictionary."""
        return {
            name: value 
            for name, value