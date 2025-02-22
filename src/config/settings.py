"""
PDF Highlighter 2.0 - Application Settings
Last Updated: 2025-02-22 21:17:16 UTC
"""

class AppConfig:
    """Application configuration settings."""
    
    # Application metadata
    APP_NAME = "PDF Highlighter"
    VERSION = "2.0.0"
    ORGANIZATION = "5446-boop"
    
    # Window settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    
    # Zoom settings
    DEFAULT_ZOOM = 1.0
    MIN_ZOOM = 0.25
    MAX_ZOOM = 5.0
    
    # Colors (RGB format, values between 0 and 1)
    DEFAULT_HIGHLIGHT_COLOR = (1, 1, 0)  # Yellow
    
    # File settings
    LOG_FILE = "pdf_highlighter.log"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'