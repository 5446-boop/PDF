"""
PDF Highlighter 2.0 - Application configuration settings.
Last Updated: 2025-02-22 20:39:07 UTC
"""

class AppConfig:
    """Application configuration."""
    
    # Application metadata
    APP_NAME = "PDF Highlighter"
    VERSION = "2.0.0"
    ORGANIZATION = "5446-boop"
    LAST_UPDATED = "2025-02-22 20:39:07"
    
    # Window settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    
    # File settings
    LOG_FILE = "pdf_highlighter.log"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Default values
    DEFAULT_ZOOM = 1.0
    DEFAULT_PAGE = 0
    MAX_ZOOM = 5.0
    MIN_ZOOM = 0.1
    
    # Colors
    DEFAULT_HIGHLIGHT_COLOR = (1, 1, 0)  # Yellow
    AVAILABLE_COLORS = [
        (1, 1, 0),    # Yellow
        (0, 1, 0),    # Green
        (1, 0, 0),    # Red
        (0, 1, 1),    # Cyan
    ]