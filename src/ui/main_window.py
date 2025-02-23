"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-23 00:47:55 UTC
"""

from src.ui.qt_imports import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QColorDialog,
    QFileDialog,
    QSplitter,
    Qt
)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.current_pdf_path = None
        self.current_color = (1, 1, 0)  # Default yellow
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PDF Highlighter")
        self.setMinimumSize(1000, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create top splitter for areas 1 and 2
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Area 1 - Control Panel (Top Left)
        self.create_control_panel(top_splitter)
        
        # Area 2 - Results Table (Top Right)
        self.create_results_table(top_splitter)
        
        # Set initial sizes for the splitter (50-50 split)
        top_splitter.setSizes([400, 400])
        
        # Add top splitter to main layout
        main_layout.addWidget(top_splitter)
        
        # Area 3 - Log Output (Bottom)
        self.create_log_panel(main_layout)
        
        # Set layout proportions (70% top, 30% bottom)
        main_layout.setStretch(0, 70)
        main_layout.setStretch(1, 30)
        
    def create_control_panel(self, parent):
        """Create the control panel (Area 1)."""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # PDF File Selection
        file_layout = QHBoxLayout()
        select_btn = QPushButton("Select PDF")
        select_btn.clicked.connect(self.select_pdf)
        file_layout.addWidget(select_btn)
        
        self.path_label = QLabel("No file selected")
        self.path_label.setWordWrap(True)
        file_layout.addWidget(self.path_label)
        layout.addLayout(file_layout)
        
        # Search Box
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_text)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Color Selection
        color_layout = QHBoxLayout()
        color_btn = QPushButton("Select Color")
        color_btn.clicked.connect(self.select_color)
        color_layout.addWidget(color_btn)
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self.update_color_preview()
        color_layout.addWidget(self.color_preview)
        layout.addLayout(color_layout)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        parent.addWidget(control_widget)
        
    def create_results_table(self, parent):
        """Create the results table (Area 2)."""
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Page", "Text", "Color"])
        self.results_table.itemDoubleClicked.connect(self.highlight_selected_text)
        
        # Set column widths
        self.results_table.setColumnWidth(0, 80)   # Page number
        self.results_table.setColumnWidth(1, 300)  # Text
        self.results_table.setColumnWidth(2, 100)  # Color
        
        parent.addWidget(self.results_table)
        
    def create_log_panel(self, layout):
        """Create the log output panel (Area 3)."""
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
    def select_pdf(self):
        """Handle PDF file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.path_label.setText(str(file_path))
            self.log_message(f"Selected PDF: {file_path}")
            
    def select_color(self):
        """Handle highlight color selection."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = (
                color.red() / 255.0,
                color.green() / 255.0,
                color.blue() / 255.0
            )
            self.update_color_preview()
            self.log_message(f"Selected color: RGB{self.current_color}")
            
    def update_color_preview(self):
        """Update the color preview label."""
        r, g, b = self.current_color
        style = f"background-color: rgb({int(r*255)}, {int(g*255)}, {int(b*255)}); border: 1px solid black;"
        self.color_preview.setStyleSheet(style)
        
    def search_text(self):
        """Handle text search."""
        text = self.search_input.text()
        if not text or not self.current_pdf_path:
            return
            
        self.log_message(f"Searching for: {text}")
        # TODO: Implement actual PDF search
        
    def highlight_selected_text(self, item):
        """Handle double-click on results table."""
        row = item.row()
        page = self.results_table.item(row, 0).text()
        text = self.results_table.item(row, 1).text()
        self.log_message(f"Highlighting text on page {page}: {text}")
        # TODO: Implement actual highlighting
        
    def log_message(self, message: str):
        """Add message to log output."""
        self.log_output.append(message)