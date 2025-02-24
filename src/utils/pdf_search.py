"""
PDF Highlighter 2.0 - PDF Search Engine
Last Updated: 2025-02-22 22:21:40 UTC
"""

import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logging.error("PyMuPDF not installed. Please install with: pip install PyMuPDF")

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class for search results."""
    page_num: int
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    highlight_color: Optional[Tuple[float, float, float]] = None  # RGB values
    annot_xref: Optional[int] = None  # Reference to the PDF annotation

class PDFSearchEngine:
    """PDF search and highlight engine."""
    
    def __init__(self):
        self.doc = None
        self.highlights: Dict[int, List[SearchResult]] = {}
        self.current_page_pixmap = None
        self.current_page_number = None
        
    def load_document(self, filepath: str) -> bool:
        """Load PDF document for searching."""
        try:
            if fitz is None:
                raise ImportError("PyMuPDF is required for PDF operations")
                
            if self.doc:
                self.doc.close()
                
            self.doc = fitz.open(filepath)
            self.highlights.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return False
    
    def add_highlight(self, page_num: int, bbox: Tuple[float, float, float, float],
                     color: Tuple[float, float, float]) -> Optional[int]:
        """
        Add highlight to specified area.
        
        Args:
            page_num: 1-based page number
            bbox: Rectangle coordinates (x0, y0, x1, y1)
            color: RGB color values (0-1 range)
            
        Returns:
            Optional[int]: Annotation reference number if successful, None if failed
        """
        try:
            if not self.doc:
                return None
                
            # Convert to 0-based page number
            page_idx = page_num - 1
            if page_idx < 0 or page_idx >= len(self.doc):
                return None
                
            page = self.doc[page_idx]
            
            # Create highlight annotation
            annot = page.add_highlight_annot(bbox)
            
            # Set highlight color and opacity
            annot.set_colors(stroke=color)
            annot.set_opacity(0.5)  # Semi-transparent highlight
            
            # Set annotation properties
            annot.update(blend_mode="Multiply")  # Better blending with text
            
            # Get the annotation reference number
            xref = annot.xref
            
            # Store highlight info
            result = SearchResult(
                page_num=page_num,
                text="",  # Text will be extracted later if needed
                bbox=bbox,
                highlight_color=color,
                annot_xref=xref
            )
            
            if page_num not in self.highlights:
                self.highlights[page_num] = []
            self.highlights[page_num].append(result)
            
            return xref
            
        except Exception as e:
            logger.error(f"Error adding highlight: {e}")
            return None
    
    def remove_highlight(self, page_num: int, xref: int) -> bool:
        """
        Remove a highlight annotation.
        
        Args:
            page_num: 1-based page number
            xref: Annotation reference number
            
        Returns:
            bool: True if highlight was removed successfully
        """
        try:
            if not self.doc:
                return False
                
            page_idx = page_num - 1
            page = self.doc[page_idx]
            
            # Find and remove the annotation
            for annot in page.annots():
                if annot.xref == xref:
                    page.delete_annot(annot)
                    
                    # Remove from our tracking
                    if page_num in self.highlights:
                        self.highlights[page_num] = [
                            h for h in self.highlights[page_num]
                            if h.annot_xref != xref
                        ]
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error removing highlight: {e}")
            return False
    
    def get_page_image(self, page_num: int, scale: float = 1.0) -> Optional[bytes]:
        """
        Get the page image with highlights rendered.
        
        Args:
            page_num: 1-based page number
            scale: Zoom scale factor
            
        Returns:
            Optional[bytes]: PNG image data if successful, None if failed
        """
        try:
            if not self.doc:
                return None
                
            page_idx = page_num - 1
            if page_idx < 0 or page_idx >= len(self.doc):
                return None
                
            page = self.doc[page_idx]
            
            # Create transformation matrix for scaling
            matrix = fitz.Matrix(scale, scale)
            
            # Render page with highlights
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert to PNG data
            return pix.tobytes("png")
            
        except Exception as e:
            logger.error(f"Error getting page image: {e}")
            return None
    
    def search_text(self, query: str, case_sensitive: bool = False) -> List[SearchResult]:
        """
        Search for text in PDF document.
        
        Args:
            query: Text to search for
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        if not self.doc or not query:
            return results
            
        try:
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                
                # Set search flags
                flags = fitz.TEXT_PRESERVE_WHITESPACE
                if not case_sensitive:
                    flags |= fitz.TEXT_DEHYPHENATE
                
                # Search for text on page with specified flags
                search_results = page.search_for(query, flags=flags)
                
                for rect in search_results:
                    # Get the text within the found rectangle
                    words = page.get_textbox(rect)
                    
                    # Check if this area is already highlighted
                    highlight_color = None
                    annot_xref = None
                    
                    if page_num + 1 in self.highlights:
                        for highlight in self.highlights[page_num + 1]:
                            if self._rectangles_overlap(rect, highlight.bbox):
                                highlight_color = highlight.highlight_color
                                annot_xref = highlight.annot_xref
                                break
                    
                    result = SearchResult(
                        page_num=page_num + 1,
                        text=words.strip(),
                        bbox=tuple(rect),
                        highlight_color=highlight_color,
                        annot_xref=annot_xref
                    )
                    results.append(result)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error searching PDF: {e}")
            return results
    
    def save_document(self, filepath: str) -> bool:
        """Save PDF with highlights."""
        try:
            if not self.doc:
                return False
                
            self.doc.save(filepath, garbage=4, deflate=True)
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            return False
    
    def _rectangles_overlap(self, rect1: tuple, rect2: tuple) -> bool:
        """Check if two rectangles overlap."""
        x1_min, y1_min, x1_max, y1_max = rect1
        x2_min, y2_min, x2_max, y2_max = rect2
        
        return not (x1_max < x2_min or x1_min > x2_max or
                   y1_max < y2_min or y1_min > y2_max)