from PyQt5 import QtWidgets, QtGui, QtCore
import fitz
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFViewer(QtWidgets.QGraphicsView):
    """
    A custom widget for displaying and navigating PDF documents.
    
    Attributes:
        page_changed = QtCore.pyqtSignal(int): Signal emitted when page changes
        zoom_changed = QtCore.pyqtSignal(float): Signal emitted when zoom changes
    """
    
    page_changed = QtCore.pyqtSignal(int)
    zoom_changed = QtCore.pyqtSignal(float)
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.initialize_variables()
        
    def setup_ui(self):
        """Initialize the UI components."""
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
    def initialize_variables(self):
        """Initialize instance variables."""
        self.pixmap_item: Optional[QtWidgets.QGraphicsPixmapItem] = None
        self.doc: Optional[fitz.Document] = None
        self.pdf_path: str = ""
        self.current_page: int = 0
        self.zoom_factor: float = 1.0
        
    def load_pdf_page(self, pdf_path: str, page_number: int = 0) -> bool:
        """
        Load and display a page from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            page_number: Page number to display (0-based).
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
                
            doc = fitz.open(str(pdf_path))
            if page_number < 0 or page_number >= len(doc):
                raise ValueError(f"Invalid page number: {page_number}")
                
            self.doc = doc
            self.pdf_path = str(pdf_path)
            self.current_page = page_number
            
            self._render_current_page()
            self.page_changed.emit(page_number)
            return True
            
        except Exception as e:
            logger.error(f"Error loading PDF page: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Could not load PDF page: {str(e)}"
            )
            return False
            
    def _render_current_page(self):
        """Render the current page with current zoom level."""
        try:
            page = self.doc.load_page(self.current_page)
            matrix = fitz.Matrix(2.0 * self.zoom_factor, 2.0 * self.zoom_factor)
            pix = page.get_pixmap(matrix=matrix)
            
            image = QtGui.QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QtGui.QImage.Format_RGBA8888
            )
            
            pixmap = QtGui.QPixmap.fromImage(image)
            self.scene.clear()
            self.pixmap_item = self.scene.addPixmap(pixmap)
            self.setSceneRect(self.scene.itemsBoundingRect())
            
        except Exception as e:
            logger.error(f"Error rendering page: {e}")
            raise
            
    def next_page(self) -> bool:
        """Move to next page if available."""
        if not self.doc or self.current_page >= len(self.doc) - 1:
            return False
        return self.load_pdf_page(self.pdf_path, self.current_page + 1)
        
    def previous_page(self) -> bool:
        """Move to previous page if available."""
        if not self.doc or self.current_page <= 0:
            return False
        return self.load_pdf_page(self.pdf_path, self.current_page - 1)
        
    def zoom_in(self):
        """Increase zoom level."""
        self.zoom_factor *= 1.2
        self._render_current_page()
        self.zoom_changed.emit(self.zoom_factor)
        
    def zoom_out(self):
        """Decrease zoom level."""
        self.zoom_factor /= 1.2
        self._render_current_page()
        self.zoom_changed.emit(self.zoom_factor)
        
    def wheelEvent(self, event: QtGui.QWheelEvent):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)