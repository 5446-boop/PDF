"""
PDF Highlighter 2.0 - PDF Handler
Last Updated: 2025-02-23 02:58:24 UTC
Author: 5446-boop
"""

import logging
import traceback
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
        self.pdf_buffer = None

    def load_document(self, filepath: str) -> bool:
        try:
            self.close()
            logger.debug(f"Attempting to load PDF: {filepath}")

            filepath = Path(filepath)
            if not filepath.is_file():
                raise PDFError(f"File not found: {filepath}")

            with open(filepath, 'rb') as file:
                self.pdf_buffer = file.read()

            self.doc = fitz.open(stream=self.pdf_buffer, filetype="pdf")
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

    def check_existing_highlight(self, page_num: int, rect: Tuple[float, float, float, float], query: str) -> Optional[Tuple[Tuple[float, float, float], int]]:
        try:
            page = self.doc[page_num - 1]
            search_rect = fitz.Rect(rect)
            search_area = search_rect.get_area()

            if search_area <= 0:
                return None

            for annot in page.annots():
                if annot.type[0] == 8:  # Highlight annotation
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

    def highlight_text(self, page_num: int, rects: List[Tuple[float, float, float, float]], color: Tuple[float, float, float], query: str) -> List[int]:
        if not self.doc:
            raise PDFError("No PDF document loaded")

        xrefs = []
        try:
            page = self.doc[page_num - 1]

            for rect in rects:
                annot = page.add_highlight_annot(rect)
                if annot:
                    annot.set_colors(stroke=color)
                    annot.update()
                    annot.set_info({"subject": query})
                    xrefs.append(annot.xref)

            return xrefs if xrefs else None

        except Exception as e:
            logger.error(f"Error adding highlights: {e}")
            return None

    def remove_highlight(self, page_num: int, xrefs: List[int]) -> bool:
        if not self.doc or not xrefs:
            return False

        try:
            page = self.doc[page_num - 1]
            success = False

            for annot in page.annots():
                if annot.xref in xrefs:
                    page.delete_annot(annot)
                    success = True

            return success

        except Exception as e:
            logger.error(f"Error removing highlights: {e}")
            return False

    def save_document(self, filepath: str) -> bool:
        if not self.doc:
            return False

        try:
            self.doc.save(filepath)
            logger.info(f"Saved PDF to: {filepath}")

            if filepath == self.filepath:
                return self.reload_document()

            return True

        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            return False

    def reload_document(self) -> bool:
        if not self.filepath:
            return False

        current_path = self.filepath
        try:
            self.load_document(current_path)
            logger.info(f"Successfully reloaded PDF from: {current_path}")
            return True
        except Exception as e:
            logger.error(f"Error reloading PDF: {e}")
            return False

    def close(self):
        try:
            if self.doc:
                self.doc.close()
            self.doc = None
            self.filepath = None
            self.pdf_buffer = None
        except Exception as e:
            logger.error(f"Error closing document: {e}")

    def __del__(self):
        self.close()

__all__ = ['PDFHandler', 'PDFError', 'SearchResult']