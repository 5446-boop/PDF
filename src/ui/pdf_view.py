"""
PDF Highlighter 2.0 - PDF View Widget
Last Updated: 2025-02-22 21:23:20 UTC
"""

import logging
from pathlib import Path

from .qt_imports import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QRubberBand, QImage, QPixmap, Qt, pyqtSignal
)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logging.error("PyMuPDF not installed. Please install with: pip install PyMuPDF")

logger = logging.getLogger(__name__)

class PDFView(QWidget):
    """Widget for displaying and interacting with PDF documents."""
    
    # Define signals
    page_changed = pyqtSignal(int, int)  # current_page, total_pages
    zoom_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize variables
        self.doc = None
        self.current_page = 0
        self.zoom_level = 1.0
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Create display label
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.display_label)
        
        layout.addWidget(self.scroll_area)
        
    def load_document(self, filepath: str) -> bool:
        """Load a PDF document."""
        if fitz is None:
            logger.error("PyMuPDF is not installed")
            return False
            
        try:
            self.doc = fitz.open(filepath)
            self.current_page = 0
            self.update_view()
            self.page_changed.emit(1, len(self.doc))
            return True
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            return False
            
    def update_view(self):
        """Update the current page view."""
        if not self.doc:
            return
            
        try:
            # Get current page
            page = self.doc[self.current_page]
            
            # Create matrix for zoom
            matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            
            # Get page pixmap
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to QImage
            img = QImage(pix.samples, pix.width, pix.height,
                        pix.stride, QImage.Format_RGB888)
            
            # Convert to QPixmap and display
            pixmap = QPixmap.fromImage(img)
            self.display_label.setPixmap(pixmap)
            
        except Exception as e:
            logger.error(f"Error updating view: {e}")
    
    def next_page(self):
        """Go to next page."""
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.update_view()
            self.page_changed.emit(self.current_page + 1, len(self.doc))
    
    def previous_page(self):
        """Go to previous page."""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.update_view()
            self.page_changed.emit(self.current_page + 1, len(self.doc))
    
    def zoom_in(self):
        """Increase zoom level."""
        self.zoom_level *= 1.2
        self.update_view()
        self.zoom_changed.emit(self.zoom_level)
    
    def zoom_out(self):
        """Decrease zoom level."""
        self.zoom_level /= 1.2
        self.update_view()
        self.zoom_changed.emit(self.zoom_level)