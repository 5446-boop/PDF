"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-22 20:41:04 UTC
Version: 2.0.0
"""

import os
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QToolBar,
    QAction, QColorDialog, QStatusBar
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSettings

from ..config import AppConfig
from .viewer import PDFViewer
from .shortcuts import Shortcuts

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings(AppConfig.ORGANIZATION, AppConfig.APP_NAME)
        self.viewer = None
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{AppConfig.APP_NAME} v{AppConfig.VERSION}")
        
        # Create PDF viewer widget
        self.viewer = PDFViewer(self)
        self.setCentralWidget(self.viewer)
        
        # Create toolbar
        self.setup_toolbar()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Setup keyboard shortcuts
        self.shortcuts = Shortcuts(self)
        
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def setup_toolbar(self):
        """Create and populate the toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Open action
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(open_action)
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_highlights)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.viewer.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.viewer.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        toolbar.addSeparator()
        
        # Color selection
        color_action = QAction("Highlight Color", self)
        color_action.triggered.connect(self.choose_color)
        toolbar.addAction(color_action)
    
    def open_pdf(self):
        """Open a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        if file_path:
            try:
                self.viewer.load_document(file_path)
                self.statusBar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                logger.error(f"Error opening PDF: {e}")
                QMessageBox.critical(self, "Error", f"Could not open PDF: {e}")
    
    def save_highlights(self):
        """Save highlighted annotations."""
        try:
            if self.viewer.save_highlights():
                self.statusBar.showMessage("Highlights saved successfully")
            else:
                self.statusBar.showMessage("No document loaded")
        except Exception as e:
            logger.error(f"Error saving highlights: {e}")
            QMessageBox.critical(self, "Error", f"Could not save highlights: {e}")
    
    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.viewer.set_highlight_color(
                (color.red() / 255.0,
                 color.green() / 255.0,
                 color.blue() / 255.0)
            )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)