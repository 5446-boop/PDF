"""
PDF Highlighter 2.0 - PDF View Widget
Last Updated: 2025-02-22 21:15:58 UTC
"""

import logging
from typing import Optional, Tuple

from src.ui.qt_imports import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QRubberBand, QImage, QPixmap, QPainter,
    Qt, pyqtSignal, QPoint, QRect, QSize
)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logging.error("PyMuPDF not installed. Please install with: pip install PyMuPDF")

from src.config.settings import AppConfig

logger = logging.getLogger(__name__)

class PDFView(QWidget):
    """Widget for displaying and interacting with PDF documents."""
    
    # Define signals
    page_changed = pyqtSignal(int, int)  # current_page, total_pages
    zoom_changed = pyqtSignal(float)
    document_loaded = pyqtSignal(int)  # total_pages
    
    def __init__(self, parent=None):
        """Initialize the PDF view widget."""
        super().__init__(parent)
        
        # Initialize variables
        self.doc = None
        self.current_page = 0
        self.zoom_level = AppConfig.DEFAULT_ZOOM
        self.highlight_mode = False
        self.highlight_color = AppConfig.DEFAULT_HIGHLIGHT_COLOR
        self.selection_start = None
        self.selection_rect = None
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Create content label
        self.content_label = QLabel(self)
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setMinimumSize(1, 1)
        self.scroll_area.setWidget(self.content_label)
        
        # Add scroll area to layout
        layout.addWidget(self.scroll_area)
        
        # Create rubber band for selection
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.content_label)
    
    def load_document(self, filepath: str) -> bool:
        """Load a PDF document."""
        if fitz is None:
            logger.error("PyMuPDF is not installed")
            return False
            
        try:
            if self.doc:
                self.doc.close()
            
            self.doc = fitz.open(filepath)
            self.current_page = 0
            self.zoom_level = AppConfig.DEFAULT_ZOOM
            self.update_view()
            self.document_loaded.emit(len(self.doc))
            return True
            
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            return False
    
    def update_view(self):
        """Update the current page view."""
        if not self.doc:
            return
            
        try:
            page = self.doc[self.current_page]
            zoom_matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convert to QImage
            img = QImage(pix.samples, pix.width, pix.height,
                        pix.stride, QImage.Format_RGB888)
            
            # Display image
            self.content_label.setPixmap(QPixmap.fromImage(img))
            
            # Emit signals
            self.page_changed.emit(self.current_page + 1, len(self.doc))
            
        except Exception as e:
            logger.error(f"Error updating view: {e}")
    
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
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.update_view()
    
    def previous_page(self):
        """Go to previous page."""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.update_view()
    
    def go_to_page(self, page_num: int):
        """Go to specific page."""
        if self.doc and 0 <= page_num < len(self.doc):
            self.current_page = page_num
            self.update_view()
    
    def set_highlight_color(self, color: Tuple[float, float, float]):
        """Set highlight color."""
        self.highlight_color = color
    
    def set_highlight_mode(self, enabled: bool):
        """Enable/disable highlight mode."""
        self.highlight_mode = enabled
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)
    
    def save_highlights(self) -> bool:
        """Save highlights to document."""
        # TODO: Implement highlight saving
        return True
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if self.highlight_mode and event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            self.rubber_band.setGeometry(QRect(self.selection_start, QSize()))
            self.rubber_band.show()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.highlight_mode and self.selection_start:
            self.rubber_band.setGeometry(
                QRect(self.selection_start, event.pos()).normalized()
            )
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if self.highlight_mode and event.button() == Qt.LeftButton:
            self.rubber_band.hide()
            selection = QRect(self.selection_start, event.pos()).normalized()
            # TODO: Convert selection to PDF coordinates and save highlight
            self.selection_start = None