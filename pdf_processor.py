"""
PDF Highlighter 2.0 - PDF Processing Module
Handles PDF document processing and highlighting operations.
"""

import fitz
import logging
from typing import Optional, List, Tuple
from pdf_utils import (
    HighlightState, 
    HighlightInfo, 
    rect_area, 
    intersection_area, 
    union_rectangles
)

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF document processing and highlighting operations."""
    
    def __init__(self):
        self.current_doc: Optional[fitz.Document] = None
        self.current_path: Optional[str] = None
    
    def open_document(self, path: str) -> bool:
        """
        Open a PDF document.
        
        Args:
            path: Path to PDF file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.current_doc = fitz.open(path)
            self.current_path = path
            return True
        except Exception as e:
            logger.error(f"Error opening PDF: {e}")
            return False
    
    def close_document(self):
        """Close the current document."""
        if self.current_doc:
            try:
                self.current_doc.close()
            except Exception as e:
                logger.error(f"Error closing PDF: {e}")
            finally:
                self.current_doc = None
                self.current_path = None
    
    def get_page(self, page_number: int) -> Optional[fitz.Page]:
        """Get a specific page from the document."""
        try:
            if self.current_doc and 0 <= page_number < len(self.current_doc):
                return self.current_doc.load_page(page_number)
        except Exception as e:
            logger.error(f"Error loading page {page_number}: {e}")
        return None

def get_occurrence_annotation_color(
    page: fitz.Page,
    occ_rects: List[fitz.Rect],
    threshold: float = 0.1
) -> Optional[Tuple[float, float, float]]:
    """
    Get the color of any existing highlight annotation for the given rectangles.
    
    Args:
        page: PDF page object.
        occ_rects: List of rectangles to check.
        threshold: Minimum overlap ratio to consider (0-1).
    
    Returns:
        Optional[Tuple[float, float, float]]: RGB color if found, None otherwise.
    """
    try:
        if not isinstance(occ_rects, (list, tuple)):
            occ_rects = [occ_rects]
            
        union = union_rectangles(occ_rects)
        if not union:
            return None
            
        best_ratio = 0.0
        best_color = None
        
        for annot in page.annots():
            if annot.type[0] != "Highlight":
                continue
                
            if not annot.colors:
                continue
                
            ratio = intersection_area(union, annot.rect) / rect_area(union)
            if ratio > best_ratio:
                best_ratio = ratio
                color = annot.colors.get("stroke") or annot.colors.get("fill")
                best_color = color
                
        return best_color if best_ratio >= threshold else None
        
    except Exception as e:
        logger.error(f"Error checking annotation color: {e}")
        return None

def toggle_highlight_on_page(
    page: fitz.Page,
    keyword: str,
    highlight_color: Optional[Tuple[float, float, float]],
    threshold: float = 0.1
) -> HighlightState:
    """
    Toggle highlight annotations for keyword occurrences on a page.
    
    Args:
        page: PDF page object.
        keyword: Text to search for.
        highlight_color: RGB color tuple for highlighting.
        threshold: Minimum overlap ratio to consider (0-1).
    
    Returns:
        HighlightState: Result of the operation.
    """
    try:
        occurrences = page.search_for(keyword)
        if not occurrences:
            return HighlightState.ERROR
            
        union = union_rectangles(occurrences)
        if not union:
            return HighlightState.ERROR
            
        existing_color = get_occurrence_annotation_color(page, occurrences, threshold)
        
        if existing_color is not None:
            # Remove existing highlights
            for annot in list(page.annots()):
                if annot.type[0] == "Highlight":
                    ratio = intersection_area(union, annot.rect) / rect_area(union)
                    if ratio >= threshold:
                        annot.delete()
            return HighlightState.REMOVED
            
        if highlight_color is None:
            return HighlightState.NO_COLOR
            
        # Add new highlights
        for occ in occurrences:
            annot = page.add_highlight_annot(occ)
            annot.set_colors(stroke=highlight_color)
            annot.info["content"] = keyword  # Store searched text
            annot.update()
        return HighlightState.ADDED
        
    except Exception as e:
        logger.error(f"Error toggling highlight: {e}")
        return HighlightState.ERROR