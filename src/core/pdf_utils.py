"""
PDF Highlighter 2.0 - PDF Utilities
Last Updated: 2025-02-22 21:03:55 UTC
"""

from dataclasses import dataclass
from typing import Tuple
import fitz

@dataclass
class HighlightInfo:
    """Store information about a highlight."""
    page: int
    rect: fitz.Rect
    color: Tuple[float, float, float]
    text: str = ""