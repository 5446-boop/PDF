"""
PDF Highlighter 2.0 - PDF Utilities Tests
Last Updated: 2025-02-22 20:43:23 UTC
Version: 2.0.0
"""

import pytest
import fitz
from src.core.pdf_utils import (
    rgb_to_hex, hex_to_rgb, HighlightInfo, 
    HighlightState, PDFError
)

def test_rgb_to_hex():
    """Test RGB to hex conversion."""
    assert rgb_to_hex((1, 1, 0)) == "#ffff00"  # Yellow
    assert rgb_to_hex((1, 0, 0)) == "#ff0000"  # Red
    assert rgb_to_hex((0, 1, 0)) == "#00ff00"  # Green
    
    with pytest.raises(ValueError):
        rgb_to_hex((1.1, 0, 0))  # Invalid RGB value

def test_hex_to_rgb():
    """Test hex to RGB conversion."""
    assert hex_to_rgb("#ffff00") == (1.0, 1.0, 0.0)  # Yellow
    assert hex_to_rgb("#ff0000") == (1.0, 0.0, 0.0)  # Red
    assert hex_to_rgb("#00ff00") == (0.0, 1.0, 0.0)  # Green
    
    with pytest.raises(ValueError):
        hex_to_rgb("#ff00")  # Invalid hex string

def test_highlight_info():
    """Test HighlightInfo validation."""
    rect = fitz.Rect(0, 0, 100, 100)
    color = (1, 1, 0)
    
    # Valid highlight
    highlight = HighlightInfo(
        page=0,
        rect=rect,
        color=color,
        state=HighlightState.COMPLETE
    )
    assert highlight.page == 0
    assert highlight.rect == rect
    assert highlight.color == color
    assert highlight.state == HighlightState.COMPLETE
    
    # Invalid page number
    with pytest.raises(ValueError):
        HighlightInfo(
            page=-1,
            rect=rect,
            color=color,
            state=HighlightState.COMPLETE
        )
    
    # Invalid color values
    with pytest.raises(ValueError):
        HighlightInfo(
            page=0,
            rect=rect,
            color=(1.1, 0, 0),
            state=HighlightState.COMPLETE
        )