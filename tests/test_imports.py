"""
PDF Highlighter 2.0 - Import Tests
Last Updated: 2025-02-22 20:50:14 UTC
Version: 2.0.0
"""

def test_imports():
    """Test that all necessary modules can be imported."""
    try:
        from src.ui import MainWindow, PDFViewer
        from src.config.settings import AppConfig
        from src.core.pdf_processor import PDFProcessor
        from src.core.pdf_utils import HighlightInfo
        
        assert MainWindow is not None
        assert PDFViewer is not None
        assert AppConfig is not None
        assert PDFProcessor is not None
        assert HighlightInfo is not None
        
    except ImportError as e:
        raise AssertionError(f"Import failed: {e}")