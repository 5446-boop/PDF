"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-22 21:20:57 UTC
"""

import logging
from pathlib import Path

from .qt_imports import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QAction, QFileDialog, QMessageBox,
    QColorDialog, QSpinBox, QLabel, QPushButton,
    QStatusBar, QSplitter, Qt, QSize, QKeySequence
)

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("PDF Highlighter")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
    def setup_ui(self):
        """Initialize the user interface."""
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # Add PDF viewer area (placeholder for now)
        self.pdf_area = QLabel("Drop a PDF file here or use File > Open")
        self.pdf_area.setAlignment(Qt.AlignCenter)
        self.pdf_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #999;
                border-radius: 8px;
                padding: 20px;
                background: #f0f0f0;
                color: #666;
            }
        """)
        content_layout.addWidget(self.pdf_area)
        
        # Add navigation controls
        nav_panel = self.create_navigation_panel()
        content_layout.addWidget(nav_panel)
        
        # Add content area to main layout
        layout.addWidget(content_area)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # File actions
        open_action = QAction("Open PDF", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # View actions
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        toolbar.addAction(zoom_out_action)
        
        toolbar.addSeparator()
        
        # Highlight actions
        highlight_action = QAction("Highlight Mode", self)
        highlight_action.setCheckable(True)
        toolbar.addAction(highlight_action)
        
        color_action = QAction("Highlight Color", self)
        toolbar.addAction(color_action)
        
    def create_navigation_panel(self):
        """Create the page navigation panel."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Previous page button
        prev_button = QPushButton("◀ Previous")
        layout.addWidget(prev_button)
        
        # Page number
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setEnabled(False)
        layout.addWidget(self.page_spin)
        
        # Total pages label
        self.total_pages = QLabel("/ 0")
        layout.addWidget(self.total_pages)
        
        # Next page button
        next_button = QPushButton("Next ▶")
        layout.addWidget(next_button)
        
        # Add stretch to push zoom control to right
        layout.addStretch()
        
        # Zoom level
        self.zoom_label = QLabel("100%")
        layout.addWidget(self.zoom_label)
        
        return panel
        
    def open_pdf(self):
        """Handle opening a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # For now, just show the filename
                name = Path(file_path).name
                self.pdf_area.setText(f"Selected: {name}")
                self.statusBar().showMessage(f"Opened: {name}")
            except Exception as e:
                logger.error(f"Error opening PDF: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not open PDF file:\n{str(e)}"
                )