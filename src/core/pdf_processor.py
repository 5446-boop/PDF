"""
PDF Highlighter 2.0 - PDF Processing Core
Last Updated: 2025-02-22 20:43:23 UTC
Version: 2.0.0
"""

import fitz
import logging
from typing import Optional, List, Dict, Tuple
from pathlib import Path

from .pdf_utils import HighlightInfo, HighlightState, PDFError

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF document processing and highlighting."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.doc: Optional[fitz.Document] = None
        self.filepath: Optional[Path] = None
        self.highlights: Dict[int, List[HighlightInfo]] = {}  # page_num -> highlights
        self._undo_stack: List[Dict] = []
        self._redo_stack: List[Dict] = []
    
    def load_document(self, filepath: str) -> bool:
        """Load a PDF document."""
        try:
            self.filepath = Path(filepath)
            self.doc = fitz.open(filepath)
            self.highlights.clear()
            self._undo_stack.clear()
            self._redo_stack.clear()
            return True
        except Exception as e:
            logger.error(f"Error loading document {filepath}: {e}")
            raise PDFError(f"Could not load PDF: {e}")
    
    def add_highlight(self, page_num: int, rect: fitz.Rect, 
                     color: Tuple[float, float, float]) -> HighlightInfo:
        """Add a highlight to the document."""
        if not self.doc:
            raise PDFError("No document loaded")
            
        if page_num < 0 or page_num >= len(self.doc):
            raise ValueError("Invalid page number")
            
        highlight = HighlightInfo(
            page=page_num,
            rect=rect,
            color=color,
            state=HighlightState.COMPLETE
        )
        
        if page_num not in self.highlights:
            self.highlights[page_num] = []
        
        # Save for undo
        self._save_undo_state()
        
        self.highlights[page_num].append(highlight)
        return highlight
    
    def remove_highlight(self, page_num: int, highlight: HighlightInfo) -> bool:
        """Remove a highlight from the document."""
        if page_num in self.highlights:
            try:
                # Save for undo
                self._save_undo_state()
                
                self.highlights[page_num].remove(highlight)
                return True
            except ValueError:
                return False
        return False
    
    def save_highlights(self) -> bool:
        """Save highlights to the PDF document."""
        if not self.doc or not self.filepath:
            return False
            
        try:
            for page_num, page_highlights in self.highlights.items():
                page = self.doc[page_num]
                for highlight in page_highlights:
                    # Add highlight annotation
                    annot = page.add_highlight_annot(highlight.rect)
                    annot.set_colors(stroke=highlight.color)
                    annot.update()
            
            # Save to file
            self.doc.save(self.filepath, incremental=True, encryption=fitz.PDF_ENCRYPT_NONE)
            return True
            
        except Exception as e:
            logger.error(f"Error saving highlights: {e}")
            raise PDFError(f"Could not save highlights: {e}")
    
    def _save_undo_state(self):
        """Save current state for undo operation."""
        state = {
            page_num: highlights.copy() 
            for page_num, highlights in self.highlights.items()
        }
        self._undo_stack.append(state)
        self._redo_stack.clear()
    
    def undo(self) -> bool:
        """Undo last highlight operation."""
        if not self._undo_stack:
            return False
            
        # Save current state for redo
        current_state = {
            page_num: highlights.copy() 
            for page_num, highlights in self.highlights.items()
        }
        self._redo_stack.append(current_state)
        
        # Restore previous state
        previous_state = self._undo_stack.pop()
        self.highlights = previous_state
        return True
    
    def redo(self) -> bool:
        """Redo last undone operation."""
        if not self._redo_stack:
            return False
            
        # Save current state for undo
        current_state = {
            page_num: highlights.copy() 
            for page_num, highlights in self.highlights.items()
        }
        self._undo_stack.append(current_state)
        
        # Restore next state
        next_state = self._redo_stack.pop()
        self.highlights = next_state
        return True