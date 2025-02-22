"""
PDF Highlighter 2.0 - PDF Utilities
Last Updated: 2025-02-22 20:39:07 UTC
Version: 2.0.0
"""

import fitz
import logging
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PDFError(Exception):
    """Base exception for PDF-related errors."""
    pass

class HighlightState(Enum):
    """Highlight states."""
    NONE = "none"
    PARTIAL = "partial"
    COMPLETE = "complete"

@dataclass
class HighlightInfo:
    """Information about a highlight."""
    page: int
    rect: fitz.Rect
    color: Tuple[float, float, float]
    state: HighlightState
    metadata: Optional[Dict] = None

    def __post_init__(self):
        """Validate highlight information."""
        if not isinstance(self.page, int) or self.page < 0:
            raise ValueError("Page must be a non-negative integer")
        if not isinstance(self.rect, fitz.Rect):
            raise ValueError("rect must be a fitz.Rect instance")
        if not all(0 <= c <= 1 for c in self.color):
            raise ValueError("Color values must be between 0 and 1")

def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    """Convert RGB color values to hex string."""
    if not all(0 <= c <= 1 for c in rgb):
        raise ValueError("RGB values must be between 0 and 1")
    return "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color string")
    r = int(hex_color[:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:], 16) / 255.0
    return (r, g, b)