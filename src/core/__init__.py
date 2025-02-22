"""
PDF Highlighter core functionality.
"""

from .pdf_utils import (
    rgb_to_hex,
    HighlightState,
    HighlightInfo
)
from .pdf_processor import PDFProcessor

__all__ = [
    'rgb_to_hex',
    'HighlightState',
    'HighlightInfo',
    'PDFProcessor'
]