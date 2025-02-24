"""
PDF Highlighter 2.0 - PDF Handler
Last Updated: 2025-02-23 11:21:30 UTC
Author: 5446-boop
"""

import logging
import traceback
import re
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
from .pdf_search import SearchResult
import fitz  # PyMuPDF

# Get module-level logger
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    page_num: int
    text: str
    rects: List[Tuple[float, float, float, float]]
    context: str
    highlight_color: Optional[Tuple[float, float, float]] = None
    annot_xrefs: List[int] = None

class PDFError(Exception):
    """Custom exception for PDF operations."""
    pass

class PDFHandler:
    def __init__(self, doc):
        self.doc = doc
        self.highlights = {}
    def search_text(self, query: str) -> List[SearchResult]:
        """Search for text in the document."""
        if not self.doc:
            logger.error("No PDF document loaded")
            raise PDFError("No PDF document loaded")
        if not query:
            logger.debug("Empty search query, returning empty results")
            return []

        page_results = {}
        delivery_pattern = re.compile(r"Delivery Number: (\d+)")
        invoice_pattern = re.compile(r"Invoice Number: (\d+)")
        
        try:
            logger.debug(f"Starting search for query: '{query}'")
            for page_num in range(len(self.doc)):
                try:
                    page = self.doc[page_num]
                    matches = page.search_for(query)

                    if matches:
                        logger.debug(f"Found {len(matches)} matches on page {page_num + 1}")
                        bboxes = []
                        xrefs = []
                        highlight_color = None
                        delivery_number = None
                        invoice_number = None

                        for rect in matches:
                            bboxes.append(tuple(rect))
                            highlight_info = self.check_existing_highlight(page_num + 1, tuple(rect), query)
                            if highlight_info:
                                color, xref = highlight_info
                                highlight_color = color
                                xrefs.append(xref)

                        expanded_rect = fitz.Rect(matches[0])
                        expanded_rect.x0 = max(0, expanded_rect.x0 - 20)
                        expanded_rect.x1 = min(page.rect.width, expanded_rect.x1 + 20)
                        expanded_rect.y0 = max(0, expanded_rect.y0 - 10)
                        expanded_rect.y1 = min(page.rect.height, expanded_rect.y1 + 10)
                        context = page.get_text("text", clip=expanded_rect).strip()
                        logger.debug(f"Got context for page {page_num + 1}: '{context[:50]}...'")
                        
                        delivery_match = delivery_pattern.search(context)
                        if delivery_match:
                            delivery_number = delivery_match.group(1)
                            
                        invoice_match = invoice_pattern.search(context)
                        if invoice_match:
                            invoice_number = invoice_match.group(1)

                        result = SearchResult(
                            page_num=page_num + 1,
                            text=query,
                            bboxes=bboxes,
                            highlight_color=highlight_color,
                            annot_xrefs=xrefs if xrefs else None,
                            delivery_number=delivery_number,
                            invoice_number=invoice_number
                        )
                        page_results[page_num + 1] = result
                        logger.debug(f"Added result for page {page_num + 1}")

                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1}: {e}")
                    continue

            results = list(page_results.values())
            logger.debug(f"Search complete - found matches on {len(results)} pages")
            return results

        except Exception as e:
            error_msg = f"Error during search: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise PDFError(f"Search failed: {str(e)}")

    def load_document(self, filepath: str) -> bool:
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
                _ = self.doc[0].get_text("text")

            logger.debug(f"Successfully loaded PDF with {total_pages} pages")
            return True

        except Exception as e:
            error_msg = f"Error loading PDF: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self.close()
            raise PDFError(f"Failed to load PDF: {str(e)}")

    def save(self) -> bool:
        """Save the document to its current location."""
        if not self.filepath:
            logger.error("No filepath set for saving")
            return False
        return self._save_document(self.filepath)

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
            temp_path = full_path + ".temp"
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

            try:
                os.replace(temp_path, full_path)
            except OSError as e:
                logger.error(f"Error replacing file: {e}")
                raise PDFError(f"Error replacing file: {e}")

            try:
                return self.load_document(full_path)
            except Exception as load_error:
                logger.error(f"Error loading saved document: {load_error}")
                if original_doc:
                    self.doc = original_doc
                return False

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

    def check_existing_highlight(self, page_num: int, rect: Tuple[float, float, float, float], query: str) -> Optional[Tuple[Tuple[float, float, float], int]]:
        """
        Check if a highlight already exists at the given location.
        
        Args:
            page_num (int): The page number to check
            rect (Tuple[float, float, float, float]): The rectangle coordinates to check
            query (str): The search query associated with the highlight
            
        Returns:
            Optional[Tuple[Tuple[float, float, float], int]]: A tuple containing the highlight color and xref if found, None otherwise
        """
        try:
            page = self.doc[page_num - 1]
            search_rect = fitz.Rect(rect)
            search_area = search_rect.get_area()

            if search_area <= 0:
                return None

            for annot in page.annots():
                if annot.type[0] == 8:  # Highlight annotation type
                    annot_rect = annot.rect
                    if search_rect.intersect(annot_rect):
                        intersection = search_rect.intersect(annot_rect)
                        intersection_area = intersection.get_area()

                        if intersection_area > 0 and (intersection_area / search_area) > 0.5:
                            if annot.info.get("subject") == query:
                                color = annot.colors['stroke'] if annot.colors else (1, 1, 0)
                                logger.debug(f"Found existing highlight on page {page_num} with color {color}")
                                return color, annot.xref

            return None

        except Exception as e:
            logger.warning(f"Error checking highlight on page {page_num}: {e}")
            return None

    def highlight_text(self, page_num: int, rects: List[Tuple[float, float, float, float]], 
                      color: Tuple[float, float, float], query: str) -> List[int]:
        """Add highlights to text on the specified page."""
        if not self.doc:
            logger.error("No PDF document loaded")
            raise PDFError("No PDF document loaded")

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
                    # Verify the annotation was actually added
                    if page.load_annot(annot.xref):
                        xrefs.append(annot.xref)
                        logger.debug(f"Added highlight annotation with xref {annot.xref}")
            
            if xrefs:
                logger.debug(f"Successfully added {len(xrefs)} highlights")
                # Use save_and_reload instead of just save
                if not self.save_and_reload():
                    logger.error("Failed to save and reload document after highlighting")
                    return None
            
            return xrefs if xrefs else None

        except Exception as e:
            logger.error(f"Error adding highlights: {e}")
            return None

    def remove_highlight(self, page_num: int, xrefs: List[int] = None) -> bool:
        """Remove all highlights from the specified page."""
        if not self.doc:
            return False

        try:
            page = self.doc[page_num - 1]
            success = False

            # Get all highlights on the page if no specific xrefs provided
            highlights_to_remove = []
            for annot in page.annots():
                if annot.type[0] == 8:  # Highlight annotation type
                    highlights_to_remove.append(annot.xref)

            if not highlights_to_remove:
                logger.debug(f"No highlights found on page {page_num}")
                return False

            # Remove all highlights
            for xref in highlights_to_remove:
                try:
                    annot = page.load_annot(xref)
                    if annot:
                        page.delete_annot(annot)
                        success = True
                        logger.debug(f"Removed highlight with xref {xref}")
                except Exception as e:
                    logger.error(f"Error removing highlight {xref}: {e}")
                    continue

            if success:
                # Save and reload after removing all highlights
                if not self.save_and_reload():
                    logger.error("Failed to save and reload document after removing highlights")
                    return False
                logger.debug(f"Successfully removed {len(highlights_to_remove)} highlights from page {page_num}")
                return True

            return success

        except Exception as e:
            logger.error(f"Error removing highlights: {e}")
            return False

    def save_and_reload(self) -> bool:
        """Save the document and reload it to ensure changes are visible."""
        if not self.filepath:
            return False
        try:
            logger.debug("Saving and reloading document")
            # Save the document
            if not self.save():
                return False
            # Reload the document to refresh its state
            return self.reload_document()
        except Exception as e:
            logger.error(f"Error in save_and_reload: {e}")
            return False

    def reload_document(self) -> bool:
        """Reload the current document to refresh its state."""
        if not self.filepath:
            return False
        try:
            logger.debug(f"Reloading document from {self.filepath}")
            # Store the current document path
            current_path = self.filepath
            # Close the current document
            self.doc.close()
            # Reopen the document
            self.doc = fitz.open(current_path)
            logger.debug("Document successfully reloaded")
            return True
        except Exception as e:
            logger.error(f"Error reloading document: {e}")
            return False

    def list_annotations(self, page_num: int):
        """List all annotations on a specific page."""
        if not self.doc:
            logger.error("No PDF document loaded")
            raise PDFError("No PDF document loaded")
        try:
            logger.debug(f"Listing annotations on page {page_num}")
            page = self.doc[page_num - 1]
            annots = []
            for annot in page.annots():
                annots.append({
                    "xref": annot.xref,
                    "type": annot.type[0],
                    "rect": annot.rect,
                    "info": annot.info
                })
            logger.debug(f"Found {len(annots)} annotations on page {page_num}")
            return annots
        except Exception as e:
            logger.error(f"Error listing annotations on page {page_num}: {e}")
            return []

    def close(self):
        """Close and clean up the document."""
        try:
            if hasattr(self, 'doc') and self.doc:
                logger.debug("Closing document")
                self.doc.close()
            self.doc = None
            self.filepath = None
        except Exception as e:
            logger.error(f"Error closing document: {e}")

    def __del__(self):
        self.close()

__all__ = ['PDFHandler', 'PDFError', 'SearchResult']