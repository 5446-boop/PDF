"""
PDF Highlighter 2.0 - PDF Handler
Last Updated: 2025-02-24 19:01:23 UTC
Author: 5446-boop
"""

import logging
import traceback
import os
import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
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
        """Format the page number as 'current/total'"""
        return f"{self.page_num}/{total_pages}"

class PDFError(Exception):
    """Custom exception for PDF operations."""
    pass

class PDFHandler:
    def __init__(self):
        self.doc = None
        self.filepath = None
        
        # Keep both patterns
        self.delivery_pattern = re.compile(
            r"Delivery(?:[-\s])?(?:No\.?|Number:?|#)?\s*(\d{5,12})",
            re.IGNORECASE | re.MULTILINE
        )
        self.number_pattern = re.compile(r'\d{8}')
        logger.debug("PDFHandler initialized with dual pattern detection")

    def _extract_invoice_number(self, page) -> Optional[str]:
        """Extract the second 8-digit number found on the page."""
        try:
            # Get all text from the page
            text = page.get_text()
            
            # Find all 8-digit numbers
            matches = self.number_pattern.findall(text)
            logger.debug(f"Found {len(matches)} 8-digit numbers: {matches}")
            
            # If we found at least two numbers
            if len(matches) >= 2:
                invoice_num = matches[1]  # Get the second number
                logger.debug(f"Using second 8-digit number as invoice number: {invoice_num}")
                return invoice_num
            elif len(matches) == 1:
                logger.debug(f"Found only one 8-digit number: {matches[0]}")
                return matches[0]
            else:
                logger.debug("No 8-digit numbers found")
                return None

        except Exception as e:
            logger.warning(f"Error extracting invoice number: {str(e)}\nTraceback:\n{traceback.format_exc()}")
            return None

    def process_page(self, page, query):
        """Process a page for highlighting."""
        try:
            text = page.get_text()
            matches = self.number_pattern.findall(text)
            
            if len(matches) >= 2:
                invoice_num = matches[1]  # Get the second number
                if query.lower() in invoice_num.lower():
                    # Create highlight for the found number
                    instances = []
                    text_instances = page.search_for(invoice_num)
                    if text_instances:
                        instances.extend(text_instances)
                    return instances
            return []

        except Exception as e:
            logger.warning(f"Error processing page {page.number}: {str(e)}")
            return []

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
                        invoice_number = self._extract_invoice_number(page)
                        delivery_match = self.delivery_pattern.search(page.get_text("text"))
                        
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

                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1}: {e}")
                    continue

            logger.info(f"Search complete - found results on {len(page_results)} pages")
            return page_results

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    def highlight_text(self, page_num: int, bboxes: List[Tuple[float, float, float, float]], 
                      color: Tuple[float, float, float], query: str) -> Optional[List[int]]:
        """Add highlights to text on the specified page."""
        if not self.doc:
            return None

        xrefs = []
        try:
            page = self.doc[page_num - 1]
            
            # Get current date and time in UTC
            import datetime
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            timestamp = f"{date_str}\n{time_str}"  # Put time under the date
            
            for rect in bboxes:
                # Create the highlight annotation (preserve original functionality)
                annot = page.add_highlight_annot(fitz.Rect(rect))
                if annot:
                    annot.set_colors(stroke=color)
                    annot.set_opacity(1)
                    annot.update()
                    xrefs.append(annot.xref)
                    
                    # Add timestamp as a free text annotation to the right of the highlight
                    timestamp_rect = fitz.Rect(
                        rect[2] + 5,           # 5 points to the right of highlight's right edge
                        rect[1] - 3,           # Slightly above highlight to be more visible
                        rect[2] + 120,         # Width for timestamp
                        rect[1] + 12           # Height for timestamp
                    )
                    
                    timestamp_annot = page.add_freetext_annot(
                        timestamp_rect,
                        timestamp,
                        fontsize=5,            # Small but visible font
                        fontname="Helvetica",
                        text_color=(1, 0, 0),  # Black text
                        fill_color=None # Light yellow background
                    )
                    
                    timestamp_annot.set_border(width=0)  # No border
                    timestamp_annot.update()
                    xrefs.append(timestamp_annot.xref)
            
            # Preserve original behavior - save the document and return xrefs
            return xrefs if self.save() else None

        except Exception as e:
            logger.error(f"Error adding highlights: {e}")
            return None

    def remove_highlight_by_text(self, page_num: int, text: str) -> bool:
        """Remove highlights for specific text on a page."""
        try:
            if not self.doc or page_num < 1:
                return False

            page = self.doc[page_num - 1]
            found = False

            for annot in page.annots():
                if annot.type[0] == 8:  # Highlight annotation
                    # Get the highlighted text
                    highlighted_text = annot.info["content"] if "content" in annot.info else ""
                    if text in highlighted_text or not highlighted_text:
                        page.delete_annot(annot)
                        found = True

            if found:
                return self.save()
            return False

        except Exception as e:
            logger.error(f"Error removing highlights: {e}")
            return False

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
            logger.debug(f"Successfully loaded PDF with {len(self.doc)} pages")
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

            self.doc.save(temp_path, garbage=0, deflate=True, clean=False)
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