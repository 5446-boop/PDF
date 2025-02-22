"""
PDF Highlighter 2.0 - Configuration
Application settings and constants.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple

@dataclass
class AppConfig:
    """Application configuration."""
    
    # Application info
    VERSION: str = "2.0"
    APP_NAME: str = "PDF Highlighter"
    ORGANIZATION: str = "5446-boop"
    
    # UI Settings
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 900
    DEFAULT_ZOOM: float = 1.0
    ZOOM_STEP: float = 0.1
    
    # PDF Settings
    DEFAULT_DPI: int = 200
    MAX_RECENT_FILES: int = 10
    
    # Colors
    DEFAULT_HIGHLIGHT_COLORS: Tuple[Tuple[float, float, float], ...] = (
        (1, 1, 0),      # Yellow
        (0.5, 1, 0.5),  # Light green
        (1, 0.7, 0.7),  # Light red
        (0.7, 0.7, 1),  # Light blue
    )
    
    # File paths
    CONFIG_DIR: Path = Path.home() / ".pdf_highlighter"
    LOG_FILE: Path = CONFIG_DIR / "pdf_highlighter.log"
    RECENT_FILES: Path = CONFIG_DIR / "recent_files.json"
    
    @classmethod
    def ensure_config_dir(cls):
        """Create configuration directory if it doesn't exist."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Create config directory on import
AppConfig.ensure_config_dir()