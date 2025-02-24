"""
PDF Highlighter 2.0 - PDF Handler
Last Updated: 2025-02-24 18:27:19 UTC
Author: 5446-boop
"""

import logging
import traceback
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
import re
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class for search results."""
    page_num: int
    text: str
    bboxes: List[Tuple[float, float, float, float]]
    total_matches: int
    highlight_color: Optional[Tuple[float, float, float]] = None
    annot_xrefs: Optional[List[int]] = None
    delivery_number: Optional[str] = None
    invoice_number: Optional[str] = None

    def format_page_number(self, total_pages: int) -> str:
        """Format page number as XXX/YYY."""
        return f"{self.page_num:03d}/{total_pages:03d}"

class PDFError(Exception):
    """Custom exception for PDF operations."""
    pass

class PDFHandler:
    def __init__(self):
        self.doc = None
        self.filepath = None
        # Compile regex patterns once at initialization for better performance
        self._compile_search_patterns()
        logger.debug("PDFHandler initialized")
    
    def _compile_search_patterns(self):
        """Compile regex patterns for invoice and delivery numbers."""
        # More comprehensive patterns for invoice number detection
        invoice_patterns = [
            r"Invoice[:\s]*(?:No\.?|Number:?|#)?\s*(\d{5,12})",  # Basic format
            r"Rechnung(?:s-?(?:nr\.?|nummer:?))?\s*(\d{5,12})",  # German format
            r"Fak(?:tura)?\.?\s*(?:nr\.?|number:?)?\s*(\d{5,12})",  # Alternative format
            r"(?:Bill|Invoice)\s*(?:#|No\.?|Number:?)?\s*[:\s]?\s*(\d{5,12})",  # Extended format
            r"(?<!\d)(\d{10})(?!\d)",  # Standalone 10-digit number
            r"F\d{2}-(\d{5,12})",  # F-prefixed format
            r"R\d{2}-(\d{5,12})"   # R-prefixed format
        ]
        
        # Combine patterns into a single regex with named groups
        self.invoice_pattern = re.compile(
            '|'.join(f'(?P<inv{i}>{pattern})' for i, pattern in enumerate(invoice_patterns)),
            re.IGNORECASE | re.MULTILINE
        )
        
        self.delivery_pattern = re.compile(
            r"Delivery(?:[-\s])?(?:No\.?|Number:?|#)?\s*(\d{5,12})",
            re.IGNORECASE | re.MULTILINE
        )
        logger.debug("Search patterns compiled")

    def search_text(self, query: str) -> List[SearchResult]:
        """Search for text in the document."""
        if not self.doc or not query:
            return []

        page_results = []
        try:
            logger.debug(f"Starting search for query: '{query}'")
            for page_num in range(len(self.doc)):
                try:
                    page = self.doc[page_num]
                    matches = page.search_for(query)

                    if matches:
                        # Get text in different formats for better extraction
                        page_text = page.get_text("text")  # Standard text
                        page_blocks = page.get_text("blocks")  # Text blocks with positioning
                        page_dict = page.get_text("dict")  # Detailed text information
                        
                        # Find invoice number using multiple approaches
                        invoice_number = self._extract_invoice_number(
                            page_text, 
                            page_blocks, 
                            page_dict,
                            matches[0]  # Use first match position as reference
                        )
                        
                        # Find delivery number (keeping existing logic)
                        delivery_match = self.delivery_pattern.search(page_text)
                        
                        result = SearchResult(
                            page_num=page_num + 1,
                            text=query,
                            bboxes=[tuple(rect) for rect in matches],
                            total_matches=len(matches),
                            highlight_color=None,
                            annot_xrefs=None,
                            delivery_number=delivery_match.group(1) if delivery_match else None,
                            invoice_number=invoice_number
                        )
                        
                        page_results.append(result)
                        logger.debug(f"Found {len(matches)} matches on page {page_num + 1}")
                        if invoice_number:
                            logger.debug(f"Found invoice number: {invoice_number}")

                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1}: {e}")
                    continue

            logger.info(f"Search complete - found results on {len(page_results)} pages")
            return page_results

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    def _extract_invoice_number(self, text: str, blocks: list, text_dict: dict, match_pos: tuple) -> Optional[str]:
        """
        Extract invoice number using multiple approaches for better reliability.
        
        Args:
            text: Raw text content of the page
            blocks: Text blocks with positioning information
            text_dict: Detailed text information dictionary
            match_pos: Position of the search match (for proximity search)
            
        Returns:
            Optional[str]: Extracted invoice number or None if not found
        """
        try:
            # Method 1: Pattern matching on full text
            for match in self.invoice_pattern.finditer(text):
                # Get the first non-None group (the actual number)
                groups = match.groups()
                for group in groups:
                    if group:
                        return group

            # Method 2: Search in nearby blocks
            match_x, match_y = match_pos[0], match_pos[1]  # Use first match position
            nearby_text = ""
            
            for block in blocks:
                # Check if block is near the match position (within 200 points)
                if isinstance(block, (tuple, list)) and len(block) >= 6:
                    block_x, block_y = block[0], block[1]
                    if abs(block_x - match_x) < 200 and abs(block_y - match_y) < 200:
                        nearby_text += block[4] if len(block) > 4 else ""

            # Search in nearby text
            if nearby_text:
                for match in self.invoice_pattern.finditer(nearby_text):
                    groups = match.groups()
                    for group in groups:
                        if group:
                            return group

            # Method 3: Look for standalone numbers in the right format
            number_pattern = re.compile(r'(?<!\d)(\d{10})(?!\d)')  # Standalone 10-digit number
            for match in number_pattern.finditer(text):
                return match.group(1)

            return None

        except Exception as e:
            logger.warning(f"Error extracting invoice number: {e}")
            return None

    def load_document(self, filepath: str) -> bool:
        """Load a PDF document from the specified filepath."""
        try:
            self.close()
            logger.debug(f"Attempting to load PDF: {filepath}")

            filepath = Path(filepath)
            if not filepath.is_file():
                logger.error(f"File not found: {filepath}")
                raise PDFError(f"File not found: {filepath}")

            self.doc = fitz.open(filepath)
            self.filepath = str(filepath)

            total_pages = len(self.doc)
            if total_pages > 0:
                _ = self.doc[0].get_text("text")  # Verify document is readable

            logger.debug(f"Successfully loaded PDF with {total_pages} pages")
            return True

        except Exception as e:
            error_msg = f"Error loading PDF: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.close()
            raise PDFError(f"Failed to load PDF: {str(e)}")

    def save(self) -> bool:
        """Save the document to its current location."""
        return self._save_document(self.filepath) if self.filepath else False

    def save_as(self, filepath: str) -> bool:
        """Save the document to a new location."""
        return self._save_document(filepath)

    def _save_document(self, filepath: str) -> bool:
        """Internal method to handle document saving."""
        if not self.doc:
            return False

        temp_path = None
        original_doc = None
        try:
            full_path = os.path.abspath(filepath)
            temp_path = f"{full_path}.temp"
            original_doc = self.doc

            self.doc.save(
                temp_path,
                garbage=0,
                deflate=True,
                clean=False,
                pretty=False,
                linear=True
            )

            self.doc.close()
            self.doc = None

            os.replace(temp_path, full_path)
            return self.load_document(full_path)

        except Exception as e:
            logger.error(f"Error saving PDF: {str(e)}")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            if original_doc:
                self.doc = original_doc
            return False

    def highlight_text(self, page_num: int, rects: List[Tuple[float, float, float, float]], 
                      color: Tuple[float, float, float], query: str) -> Optional[List[int]]:
        """Add highlights to text on the specified page."""
        if not self.doc:
            return None

        xrefs = []
        try:
            logger.debug(f"Adding highlights on page {page_num} for query: '{query}'")
            page = self.doc[page_num - 1]
            
            for rect in rects:
                annot = page.add_highlight_annot(fitz.Rect(rect))
                if annot and annot.type[0] == 8:  # Verify it's a highlight annotation
                    annot.set_colors(stroke=color)
                    annot.set_opacity(0.5)
                    annot.set_info({"subject": query, "title": "Highlight"})
                    annot.update()
                    if page.load_annot(annot.xref):
                        xrefs.append(annot.xref)
            
            if xrefs and self.save_and_reload():
                logger.debug(f"Successfully added {len(xrefs)} highlights")
                return xrefs
            
            return None

        except Exception as e:
            logger.error(f"Error adding highlights: {e}")
            return None

    def remove_highlight(self, page_num: int, xrefs: List[int]) -> bool:
        """Remove specified highlights from the page."""
        if not self.doc:
            logger.error("No PDF document loaded")
            return False

        try:
            logger.debug(f"Removing highlights on page {page_num} with xrefs: {xrefs}")
            page = self.doc[page_num - 1]
            success = False

            for xref in xrefs:
                try:
                    annot = page.load_annot(xref)
                    if annot and annot.type[0] == 8:  # Highlight annotation
                        page.delete_annot(annot)
                        success = True
                        logger.debug(f"Removed highlight with xref {xref}")
                except Exception as e:
                    logger.error(f"Error removing highlight {xref}: {e}")
                    continue

            if success and self.save():
                logger.debug("Successfully saved document after removing highlights")
                return True
            return False

        except Exception as e:
            logger.error(f"Error removing highlights: {e}")
            return False

    def remove_highlight_by_text(self, page_num: int, text: str) -> bool:
        """Remove highlights from page that match the given text."""
        if not self.doc:
            logger.error("No PDF document loaded")
            return False

        try:
            logger.debug(f"Removing highlights for text '{text}' on page {page_num}")
            page = self.doc[page_num - 1]
            success = False

            # Get all highlights on the page
            for annot in page.annots():
                if annot.type[0] == 8:  # Highlight annotation
                    # Check if this highlight is for our search text
                    if annot.info.get("subject") == text:
                        page.delete_annot(annot)
                        success = True
                        logger.debug(f"Removed highlight for text '{text}'")

            if success and self.save():
                logger.debug("Successfully saved document after removing highlights")
                return True
            return False

        except Exception as e:
            logger.error(f"Error removing highlights: {e}")
            return False   

    def save_and_reload(self) -> bool:
        """Save the document and reload it to ensure changes are visible."""
        return self.save() and self.reload_document() if self.filepath else False

    def reload_document(self) -> bool:
        """Reload the current document to refresh its state."""
        if not self.filepath:
            return False
        try:
            current_path = self.filepath
            self.doc.close()
            self.doc = fitz.open(current_path)
            logger.debug("Document successfully reloaded")
            return True
        except Exception as e:
            logger.error(f"Error reloading document: {e}")
            return False

    def close(self) -> None:
        """Close and clean up the document."""
        try:
            if self.doc:
                self.doc.close()
            self.doc = None
            self.filepath = None
        except Exception as e:
            logger.error(f"Error closing document: {e}")

    def __del__(self):
        """Ensure document is closed when object is destroyed."""
        self.close()

__all__ = ['PDFHandler', 'PDFError', 'SearchResult']