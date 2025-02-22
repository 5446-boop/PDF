"""
PDF Highlighter 2.0 - Application Settings
Last Updated: 2025-02-22 20:48:47 UTC
Version: 2.0.0
"""

from pathlib import Path

class AppConfig:
    """Application configuration settings."""
    
    # Application metadata
    APP_NAME = "PDF Highlighter"
    VERSION = "2.0.0"
    ORGANIZATION = "5446-boop"
    LAST_UPDATED = "2025-02-22 20:48:47"
    
    # Window settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    
    # File settings
    LOG_FILE = "pdf_highlighter.log"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Paths
    APP_DIR = Path(__file__).parent.parent.parent
    RESOURCES_DIR = APP_DIR / "resources"
    
    # Audio files
    MATCH_FOUND_SOUND = str(RESOURCES_DIR / "match_found_soft.wav")
    NO_MATCH_SOUND = str(RESOURCES_DIR / "no_match_soft.wav")
    
    # PDF settings
    DEFAULT_ZOOM = 1.0
    DEFAULT_PAGE = 0
    MAX_ZOOM = 5.0
    MIN_ZOOM = 0.1
    
    # Colors (RGB format, values between 0 and 1)
    DEFAULT_HIGHLIGHT_COLOR = (1, 1, 0)  # Yellow
    AVAILABLE_COLORS = [
        (1, 1, 0),    # Yellow
        (0, 1, 0),    # Green
        (1, 0, 0),    # Red
        (0, 1, 1),    # Cyan
    ]