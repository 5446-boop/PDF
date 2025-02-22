"""
PDF Highlighter 2.0 - PDF Utilities
Last Updated: 2025-02-22
"""

import fitz
import logging
from typing import List, Optional, Tuple
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

def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    """Convert RGB color values to hex string."""
    if not all(0 <= c <= 1 for c in rgb):
        raise ValueError("RGB values must be between 0 and 1")
    return "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

def rect_area(rect: fitz.Rect) -> float:
    """Calculate the area of a rectangle."""
    try:
        return max(0, rect.x1 - rect.x0) * max(0, rect.y1 - rect.y0)
    except AttributeError as e:
        logger.error(f"Invalid rectangle object: {e}")
        raise PDFError("Invalid rectangle object") from e

def intersection_area(rect1: fitz.Rect, rect2: fitz.Rect) -> float:
    """Calculate the intersection area of two rectangles."""
    try:
        inter = rect1.intersect(rect2)
        if inter is None:
            return 0
        return rect_area(inter)
    except AttributeError as e:
        logger.error(f"Invalid rectangle object: {e}")
        raise PDFError("Invalid rectangle object") from e