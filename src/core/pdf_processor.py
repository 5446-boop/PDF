"""
PDF processing functionality.
"""
import logging
from pathlib import Path
from typing import Optional, List, Tuple
import fitz

from .pdf_utils import HighlightInfo, HighlightState

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF document processing and highlighting."""
    
    def __init__(self, filepath: Optional[str] = None):
        self.doc = None
        self.filepath = None
        if filepath:
            self.load_document(filepath)
    
    def load_document(self, filepath: str) -> bool:
        """Load a PDF document."""
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"PDF file not found: {filepath}")
            
            self.doc = fitz.open(str(path))
            self.filepath = str(path)
            return True
            
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return False
    
    def save_document(self, output_path: Optional[str] = None) -> bool:
        """Save the PDF document."""
        try:
            save_path = output_path or self.filepath
            self.doc.save(save_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            return True
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            return False
    
    def close(self):
        """Close the PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None