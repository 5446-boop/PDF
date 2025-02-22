"""
PDF Highlighter 2.0 - PDF Viewer Widget
Last Updated: 2025-02-22 20:50:14 UTC
Version: 2.0.0
"""

import logging
from typing import Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect

from src.core.pdf_processor import PDFProcessor
from src.core.pdf_utils import HighlightInfo, HighlightState
from src.config.settings import AppConfig

logger = logging.getLogger(__name__)

class PDFViewer(QWidget):
    """PDF viewer widget with highlighting capability."""
    
    # Signals
    page_changed = pyqtSignal(int, int)  # current_page, total_pages
    zoom_changed = pyqtSignal(float)
    highlight_added = pyqtSignal(HighlightInfo)
    highlight_removed = pyqtSignal(HighlightInfo)
    
    def __init__(self, parent=None):
        """Initialize the PDF viewer."""
        super().__init__(parent)
        self.processor = PDFProcessor()
        self.current_page = 0
        self.zoom_level = AppConfig.DEFAULT_ZOOM
        self.highlight_color = AppConfig.DEFAULT_HIGHLIGHT_COLOR
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for PDF content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Label for displaying PDF page
        self.page_label = QLabel(self)
        self.page_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.page_label)
        
        self.layout.addWidget(self.scroll_area)
    
    def load_document(self, filepath: str) -> bool:
        """Load a PDF document."""
        try:
            if self.processor.load_document(filepath):
                self.current_page = AppConfig.DEFAULT_PAGE
                self.zoom_level = AppConfig.DEFAULT_ZOOM
                self.update_view()
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            raise
    
    def update_view(self):
        """Update the current page view."""
        if not self.processor.doc:
            return
            
        try:
            # Get page image
            page = self.processor.doc[self.current_page]
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
            
            # Convert to QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            # Display image
            self.page_label.setPixmap(QPixmap.fromImage(img))
            
            # Update page count
            total_pages = len(self.processor.doc)
            self.page_changed.emit(self.current_page + 1, total_pages)
            
        except Exception as e:
            logger.error(f"Error updating view: {e}")
            raise
    
    def zoom_in(self):
        """Increase zoom level."""
        if self.zoom_level < AppConfig.MAX_ZOOM:
            self.zoom_level *= 1.2
            self.zoom_changed.emit(self.zoom_level)
            self.update_view()
    
    def zoom_out(self):
        """Decrease zoom level."""
        if self.zoom_level > AppConfig.MIN_ZOOM:
            self.zoom_level /= 1.2
            self.zoom_changed.emit(self.zoom_level)
            self.update_view()
    
    def next_page(self):
        """Go to next page."""
        if self.processor.doc and self.current_page < len(self.processor.doc) - 1:
            self.current_page += 1
            self.update_view()
    
    def previous_page(self):
        """Go to previous page."""
        if self.processor.doc and self.current_page > 0:
            self.current_page -= 1
            self.update_view()
    
    def set_highlight_color(self, color: Tuple[float, float, float]):
        """Set the current highlight color."""
        self.highlight_color = color

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()