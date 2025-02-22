"""
PDF Highlighter 2.0 - Application configuration settings.
Last Updated: 2025-02-22
"""

class AppConfig:
    """Application configuration."""
    
    # Application metadata
    APP_NAME = "PDF Highlighter"
    VERSION = "2.0.0"
    ORGANIZATION = "5446-boop"
    LAST_UPDATED = "2025-02-22"
    
    # Window settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # File settings
    LOG_FILE = "pdf_highlighter.log"
    
    # Default values
    DEFAULT_ZOOM = 1.0
    DEFAULT_PAGE = 0
    
    # Colors
    DEFAULT_HIGHLIGHT_COLOR = (1, 1, 0)  # Yellow