"""
PDF Highlighter 2.0 - PDF Processor Tests
Last Updated: 2025-02-22 20:43:23 UTC
Version: 2.0.0
"""

import pytest
import fitz
from pathlib import Path
from src.core.pdf_processor import PDFProcessor
from src.core.pdf_utils import PDFError, HighlightState

@pytest.fixture
def processor():
    """Create a PDF processor instance."""
    return PDFProcessor()

def test_load_document(processor, tmp_path):
    """Test loading a PDF document."""
    # Create a test PDF
    doc = fitz.open()
    doc.new_page()
    test_pdf = tmp_path / "test.pdf"
    doc.save(test_pdf)
    
    assert processor.load_document(str(test_pdf))
    assert processor.doc is not None
    assert processor.filepath == Path(test_pdf)
    
    # Test invalid file
    with pytest.raises(PDFError):
        processor.load_document("nonexistent.pdf")

def test_add_highlight(processor, tmp_path):
    """Test adding highlights."""
    # Create a test PDF
    doc = fitz.open()
    doc.new_page()
    test_pdf = tmp_path / "test.pdf"
    doc.save(test_pdf)
    
    processor.load_document(str(test_pdf))
    
    rect = fitz.Rect(0, 0, 100, 100)
    color = (1, 1, 0)
    
    highlight = processor.add_highlight(0, rect, color)
    assert highlight.page == 0
    assert highlight.rect == rect
    assert highlight.color == color
    assert highlight.state == HighlightState.COMPLETE
    
    # Test invalid page number
    with pytest.raises(ValueError):
        processor.add_highlight(-1, rect, color)

def test_undo_redo(processor, tmp_path):
    """Test undo/redo functionality."""
    # Create a test PDF
    doc = fitz.open()
    doc.new_page()
    test_pdf = tmp_path / "test.pdf"
    doc.save(test_pdf)
    
    processor.load_document(str(test_pdf))
    
    # Add a highlight
    rect = fitz.Rect(0, 0, 100, 100)
    color = (1, 1, 0)
    processor.add_highlight(0, rect, color)
    
    # Undo
    assert processor.undo()
    assert len(processor.highlights.get(0, [])) == 0
    
    # Redo
    assert processor.redo()
    assert len(processor.highlights.get(0, [])) == 1