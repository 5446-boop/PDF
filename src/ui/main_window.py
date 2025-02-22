"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-22 21:23:20 UTC
"""

# ... [previous imports remain the same]
from .pdf_view import PDFView

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()
        
    # ... [previous methods remain the same until setup_ui]
    
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
        
        # Create PDF viewer
        self.pdf_view = PDFView()
        content_layout.addWidget(self.pdf_view)
        
        # Add navigation controls
        nav_panel = self.create_navigation_panel()
        content_layout.addWidget(nav_panel)
        
        # Add content area to main layout
        layout.addWidget(content_area)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Connect signals
        self.connect_signals()
        
    def connect_signals(self):
        """Connect all signals."""
        # Connect PDF view signals
        self.pdf_view.page_changed.connect(self.update_page_info)
        self.pdf_view.zoom_changed.connect(self.update_zoom_info)
        
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
        zoom_in_action.triggered.connect(self.pdf_view.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.pdf_view.zoom_out)
        toolbar.addAction(zoom_out_action)
        
    def create_navigation_panel(self):
        """Create the page navigation panel."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Previous page button
        prev_button = QPushButton("◀ Previous")
        prev_button.clicked.connect(self.pdf_view.previous_page)
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
        next_button.clicked.connect(self.pdf_view.next_page)
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
                if self.pdf_view.load_document(file_path):
                    name = Path(file_path).name
                    self.statusBar().showMessage(f"Opened: {name}")
            except Exception as e:
                logger.error(f"Error opening PDF: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not open PDF file:\n{str(e)}"
                )
                
    def update_page_info(self, current_page, total_pages):
        """Update page navigation controls."""
        self.page_spin.setEnabled(True)
        self.page_spin.setMaximum(total_pages)
        self.page_spin.setValue(current_page)
        self.total_pages.setText(f"/ {total_pages}")
        
    def update_zoom_info(self, zoom_level):
        """Update zoom level display."""
        percentage = int(zoom_level * 100)
        self.zoom_label.setText(f"{percentage}%")