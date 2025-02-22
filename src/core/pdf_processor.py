"""
PDF Highlighter 2.0 - PDF Processor
Last Updated: 2025-02-22 21:03:55 UTC
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fitz

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF document processing and highlighting."""
    
    def __init__(self):
        self.doc = None
        self.highlights: Dict[int, List] = {}  # page_num -> list of highlights
        self.current_path = None
    
    def load_document(self, filepath: str) -> bool:
        """Load a PDF document."""
        try:
            if self.doc:
                self.doc.close()
            
            self.doc = fitz.open(filepath)
            self.current_path = filepath
            self.highlights.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            return False
    
    def close(self):
        """Close the current document."""
        if self.doc:
            try:
                self.doc.close()
                self.doc = None
                self.current_path = None
                self.highlights.clear()
            except Exception as e:
                logger.error(f"Error closing document: {e}")