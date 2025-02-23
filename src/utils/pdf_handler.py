"""
PDF Highlighter 2.0 - PDF Handler
Last Updated: 2025-02-23 04:37:13 UTC
Author: 5446-boop
"""

import logging
import traceback
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
import fitz  # PyMuPDF

logging.basicConfig(level=logging.DEBUG)
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
    def __init__(self):
        self.doc = None
        self.filepath = None

    def load_document(self, filepath: str) -> bool:
        try:
            self.close()
            logger.debug(f"Attempting to load PDF: {filepath}")

            filepath = Path(filepath)
            if not filepath.is_file():
                raise PDFError(f"File not found: {filepath}")

            self.doc = fitz.open(filepath)
            self.filepath = str(filepath)

            total_pages = len(self.doc)
            if total_pages > 0:
                _ = self.doc[0].get_text("text")

            logger.info(f"Successfully loaded PDF with {total_pages} pages")
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

    def highlight_text(self, page_num: int, rects: List[Tuple[float, float, float, float]], 
                      color: Tuple[float, float, float], query: str) -> List[int]:
        if not self.doc:
            raise PDFError("No PDF document loaded")

        xrefs = []
        try:
            page = self.doc[page_num - 1]
            for rect in rects:
                annot = page.add_highlight_annot(fitz.Rect(rect))
                if annot:
                    annot.set_colors(stroke=color)
                    annot.set_opacity(0.5)
                    annot.set_info({"subject": query, "title": "Highlight"})
                    annot.update()
                    xrefs.append(annot.xref)
            
            if xrefs:
                if not self.save():
                    logger.error("Failed to save document after highlighting")
                    return None
            
            return xrefs if xrefs else None

        except Exception as e:
            logger.error(f"Error adding highlights: {e}")
            return None

    def check_existing_highlight(self, page_num: int, rect: Tuple[float, float, float, float], query: str) -> Optional[Tuple[Tuple[float, float, float], int]]:
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
                                return color, annot.xref

            return None

        except Exception as e:
            logger.warning(f"Error checking highlight on page {page_num}: {e}")
            return None

    def remove_highlight(self, page_num: int, xrefs: List[int]) -> bool:
        if not self.doc or not xrefs:
            return False

        try:
            page = self.doc[page_num - 1]
            success = False

            for xref in xrefs:
                try:
                    annot = page.load_annot(xref)
                    if annot:
                        page.delete_annot(annot)
                        success = True
                except Exception as e:
                    logger.error(f"Error loading annotation {xref}: {e}")

            if success:
                if not self.save():
                    logger.error("Failed to save document after removing highlights")
                    return False

                self.doc.reload_page(page_num - 1)
                return True

            return success

        except Exception as e:
            logger.error(f"Error removing highlights: {e}")
            return False

    def search_text(self, query: str) -> List[SearchResult]:
        if not self.doc:
            raise PDFError("No PDF document loaded")
        if not query:
            return []

        page_results = {}
        try:
            logger.debug(f"Searching for: {query}")
            for page_num in range(len(self.doc)):
                try:
                    page = self.doc[page_num]
                    matches = page.search_for(query)

                    if matches:
                        rects = []
                        xrefs = []
                        highlight_color = None

                        for rect in matches:
                            rects.append(tuple(rect))
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

                        result = SearchResult(
                            page_num=page_num + 1,
                            text=query,
                            rects=rects,
                            context=context,
                            highlight_color=highlight_color,
                            annot_xrefs=xrefs if xrefs else None
                        )
                        page_results[page_num + 1] = result

                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1}: {e}")
                    continue

            results = list(page_results.values())
            logger.debug(f"Found matches on {len(results)} pages")
            return results

        except Exception as e:
            error_msg = f"Error during search: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise PDFError(f"Search failed: {str(e)}")

    def list_annotations(self, page_num: int):
        if not self.doc:
            raise PDFError("No PDF document loaded")
        try:
            page = self.doc[page_num - 1]
            annots = []
            for annot in page.annots():
                annots.append({
                    "xref": annot.xref,
                    "type": annot.type[0],
                    "rect": annot.rect,
                    "info": annot.info
                })
            return annots
        except Exception as e:
            logger.error(f"Error listing annotations on page {page_num}: {e}")
            return []

    def close(self):
        """Close and clean up the document."""
        try:
            if hasattr(self, 'doc') and self.doc:
                self.doc.close()
            self.doc = None
            self.filepath = None
        except Exception as e:
            logger.error(f"Error closing document: {e}")

    def __del__(self):
        self.close()

__all__ = ['PDFHandler', 'PDFError', 'SearchResult']