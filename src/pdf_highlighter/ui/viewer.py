"""
PDF Highlighter 2.0 - PDF Viewer
PDF-visningskomponent med zoom og navigasjon.
"""

from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QMessageBox
)
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, pyqtSignal

import fitz

class PDFViewer(QGraphicsView):
    # Signaler
    page_changed = pyqtSignal(int)  # Når siden endres
    zoom_changed = pyqtSignal(float)  # Når zoom endres
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Innstillinger for visning
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(Qt.gray)
        
        # PDF-variabler
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.pixmap_item = None
        
    def load_pdf(self, path: str):
        """Last inn PDF-fil."""
        try:
            self.doc = fitz.open(path)
            self.total_pages = len(self.doc)
            self.current_page = 0
            self.load_current_page()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Feil",
                f"Kunne ikke laste PDF: {e}"
            )
            
    def load_current_page(self):
        """Last inn gjeldende side."""
        if not self.doc:
            return
            
        try:
            page = self.doc.load_page(self.current_page)
            zoom_matrix = fitz.Matrix(2.0 * self.zoom_factor, 2.0 * self.zoom_factor)
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            image = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format_RGB888
            )
            
            self.scene.clear()
            self.pixmap_item = self.scene.addPixmap(QPixmap.fromImage(image))
            self.setSceneRect(self.scene.itemsBoundingRect())
            self.centerOn(self.pixmap_item)
            
            self.page_changed.emit(self.current_page)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Feil",
                f"Kunne ikke laste side: {e}"
            )
            
    def next_page(self):
        """Gå til neste side."""
        if self.doc and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_current_page()
            
    def previous_page(self):
        """Gå til forrige side."""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.load_current_page()
            
    def zoom_in(self):
        """Zoom inn."""
        self.zoom_factor *= 1.2
        self.zoom_changed.emit(self.zoom_factor)
        self.load_current_page()
        
    def zoom_out(self):
        """Zoom ut."""
        self.zoom_factor /= 1.2
        self.zoom_changed.emit(self.zoom_factor)
        self.load_current_page()
        
    def fit_width(self):
        """Tilpass bredden til vinduet."""
        if self.pixmap_item:
            viewport_width = self.viewport().width()
            content_width = self.pixmap_item.boundingRect().width()
            self.zoom_factor *= viewport_width / content_width
            self.zoom_changed.emit(self.zoom_factor)
            self.load_current_page()
            
    def search_text(self, keyword: str) -> list:
        """
        Søk etter tekst på gjeldende side.
        Returnerer en liste med søkeresultater.
        """
        results = []
        if not self.doc:
            return results
            
        page = self.doc.load_page(self.current_page)
        areas = page.search_for(keyword)
        
        for area in areas:
            # Hent litt kontekst rundt treffet
            words = page.get_text("words")
            context = self.get_text_context(words, area)
            
            results.append({
                'page': self.current_page,
                'keyword': keyword,
                'context': context,
                'status': 'Funnet',
                'rect': area
            })
            
        return results
        
    def get_text_context(self, words, area, context_words=5):
        """Hent tekstkontekst