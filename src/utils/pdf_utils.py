import fitz  # PyMuPDF
import logging
from typing import List, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFError(Exception):
    """Base exception for PDF-related errors."""
    pass

def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    """
    Convert RGB color values to hex string.
    
    Args:
        rgb: Tuple of (red, green, blue) values between 0 and 1.
    
    Returns:
        str: Hex color string (e.g., "#ff0000" for red).
    
    Raises:
        ValueError: If RGB values are not between 0 and 1.
    """
    if not all(0 <= c <= 1 for c in rgb):
        raise ValueError("RGB values must be between 0 and 1")
    
    return "#%02x%02x%02x" % (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def union_rectangles(rects: List[fitz.Rect]) -> Optional[fitz.Rect]:
    """
    Calculate the union of multiple rectangles.
    
    Args:
        rects: List of fitz.Rect objects.
    
    Returns:
        Optional[fitz.Rect]: Combined rectangle or None if input is empty.
    """
    if not rects:
        logger.debug("Empty rectangle list provided")
        return None
        
    try:
        x0 = min(r.x0 for r in rects)
        y0 = min(r.y0 for r in rects)
        x1 = max(r.x1 for r in rects)
        y1 = max(r.y1 for r in rects)
        return fitz.Rect(x0, y0, x1, y1)
    except AttributeError as e:
        logger.error(f"Invalid rectangle object in list: {e}")
        raise PDFError("Invalid rectangle object") from e

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
        raise PDFError("Invalid rectangle object") from e

def rect_area(rect: fitz.Rect) -> float:
    """
    Calculate the area of a rectangle.
    
    Args:
        rect: Source rectangle.
    
    Returns:
        float: Area of the rectangle.
    """
    try:
        return max(0, rect.x1 - rect.x0) * max(0, rect.y1 - rect.y0)
    except AttributeError as e:
        logger.error(f"Invalid rectangle object: {e}")
        raise PDFError("Invalid rectangle object") from e

def intersection_area(rect1: fitz.Rect, rect2: fitz.Rect) -> float:
    """
    Calculate the intersection area of two rectangles.
    
    Args:
        rect1: First rectangle.
        rect2: Second rectangle.
    
    Returns:
        float: Area of intersection (0 if no intersection).
    """
    try:
        inter = rect1.intersect(rect2)
        if inter is None:
            return 0
        return rect_area(inter)
    except AttributeError as e:
        logger.error(f"Invalid rectangle object: {e}")
        raise PDFError("Invalid rectangle objects") from e