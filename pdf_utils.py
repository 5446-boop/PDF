"""
PDF Highlighter 2.0 - Utility Functions
Provides utility functions for PDF handling and color management.
"""

import fitz
import logging
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class HighlightState(Enum):
    """Enumeration for highlight states."""
    ADDED = "added"
    REMOVED = "removed"
    NO_COLOR = "no_color"
    ERROR = "error"

@dataclass
class HighlightInfo:
    """Container for highlight information."""
    page_number: int
    text: str
    color: Optional[Tuple[float, float, float]]
    rects: List[fitz.Rect]

def rgb_to_hex(rgb: Optional[Tuple[float, float, float]]) -> str:
    """
    Convert RGB color values (0-1) to hex string.
    
    Args:
        rgb: Tuple of (red, green, blue) values between 0 and 1.
    
    Returns:
        str: Hex color string (e.g., "#ff0000" for red) or "none" if rgb is None.
    
    Raises:
        ValueError: If RGB values are not between 0 and 1.
    """
    if rgb is None:
        return "none"
        
    if not all(0 <= c <= 1 for c in rgb):
        raise ValueError("RGB values must be between 0 and 1")
    
    return "#%02x%02x%02x" % tuple(int(c * 255) for c in rgb)

def union_rectangles(rects: List[fitz.Rect]) -> Optional[fitz.Rect]:
    """
    Calculate the union of multiple rectangles.
    
    Args:
        rects: List of fitz.Rect objects.
    
    Returns:
        Optional[fitz.Rect]: Combined rectangle or None if input is empty.
    """
    if not rects:
        return None
        
    try:
        return fitz.Rect(
            min(r.x0 for r in rects),
            min(r.y0 for r in rects),
            max(r.x1 for r in rects),
            max(r.y1 for r in rects)
        )
    except AttributeError as e:
        logger.error(f"Invalid rectangle object: {e}")
        return None

def inflate_rect(rect: fitz.Rect, amount: float) -> fitz.Rect:
    """
    Expand a rectangle by a given amount in all directions.
    
    Args:
        rect: Source rectangle.
        amount: Amount to expand by (can be negative to shrink).
    
    Returns:
        fitz.Rect: New expanded rectangle.
    """
    try:
        return fitz.Rect(
            rect.x0 - amount,
            rect.y0 - amount,
            rect.x1 + amount,
            rect.y1 + amount
        )
    except AttributeError as e:
        logger.error(f"Invalid rectangle object: {e}")
        raise ValueError("Invalid rectangle object") from e

def get_page_text_words(page: fitz.Page) -> List[Dict]:
    """
    Get all words on a page with their positions.
    
    Args:
        page: PDF page object.
    
    Returns:
        List[Dict]: List of dictionaries containing word information.
    """
    try:
        words = page.get_text("words")
        return [
            {
                "text": word[4],
                "rect": fitz.Rect(word[:4]),
                "block_no": word[5],
                "line_no": word[6],
                "word_no": word[7]
            }
            for word in words
        ]
    except Exception as e:
        logger.error(f"Error getting page words: {e}")
        return []

def extract_page_highlights(page: fitz.Page) -> List[HighlightInfo]:
    """
    Extract all highlights from a page.
    
    Args:
        page: PDF page object.
    
    Returns:
        List[HighlightInfo]: List of highlight information.
    """
    highlights = []
    try:
        for annot in page.annots():
            if annot.type[0] == "Highlight":
                color = annot.colors.get("stroke") or annot.colors.get("fill")
                text = annot.info.get("content", "")
                highlights.append(HighlightInfo(
                    page_number=page.number,
                    text=text,
                    color=color,
                    rects=[annot.rect]
                ))
    except Exception as e:
        logger.error(f"Error extracting highlights: {e}")
    
    return highlights

def rect_area(rect: fitz.Rect) -> float:
    """Calculate the area of a rectangle."""
    try:
        return max(0, rect.x1 - rect.x0) * max(0, rect.y1 - rect.y0)
    except AttributeError:
        return 0

def intersection_area(rect1: fitz.Rect, rect2: fitz.Rect) -> float:
    """Calculate the intersection area of two rectangles."""
    try:
        inter = rect1.intersect(rect2)
        return rect_area(inter) if inter else 0
    except AttributeError:
        return 0