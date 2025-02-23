"""
PDF Highlighter 2.0 - UI Components
Last Updated: 2025-02-23 11:38:03 UTC
Author: 5446-boop
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit,
    QTextEdit, QSplitter, QCheckBox,
    QMenuBar, QMenu, QAction
)
from PyQt5.QtCore import Qt

from .widgets.color_picker import ColorPicker
from .widgets.results_table import ResultsTable

def setup_ui_components(window):
    """Setup all UI components for the main window."""
    # Create menu bar
    create_menu_bar(window)
    
    # Create main widget and layout
    main_widget = QWidget()
    window.setCentralWidget(main_widget)
    main_layout = QVBoxLayout(main_widget)
    
    # Create left panel
    left_panel = create_left_panel(window)
    
    # Create right panel
    right_panel = create_right_panel(window)
    
    # Create splitter and add panels
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([400, 600])
    
    # Add splitter and results table to main layout
    main_layout.addWidget(splitter)
    
    # Create results table
    window.results_table = ResultsTable()
    main_layout.addWidget(window.results_table)

def create_menu_bar(window):
    """Create the menu bar with File and Settings menus."""
    menubar = window.menuBar()
    
    # File Menu
    file_menu = menubar.addMenu('File')
    
    exit_action = QAction('Exit', window)
    exit_action.setShortcut('Ctrl+Q')
    exit_action.triggered.connect(window.close)
    file_menu.addAction(exit_action)
    
    # Settings Menu (right-aligned)
    settings_menu = QMenu('Settings', window)
    about_action = QAction('About', window)
    about_action.triggered.connect(window.show_about_dialog)
    settings_menu.addAction(about_action)
    
    menubar.addMenu(settings_menu)

def create_left_panel(window):
    """Create the left panel with file selection and search controls."""
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    
    # File selection
    file_group = QWidget()
    file_layout = QHBoxLayout(file_group)
    window.select_btn = QPushButton("Select PDF")
    window.select_btn.clicked.connect(window.select_pdf)
    file_layout.addWidget(window.select_btn)
    
    window.path_label = QLabel("No file selected")
    window.path_label.setWordWrap(True)
    file_layout.addWidget(window.path_label)
    left_layout.addWidget(file_group)
    
    # Search
    search_group = QWidget()
    search_layout = QHBoxLayout(search_group)
    window.search_input = QLineEdit()
    window.search_input.setPlaceholderText("Enter search text...")
    search_layout.addWidget(window.search_input)
    
    window.search_btn = QPushButton("Search")
    window.search_btn.clicked.connect(window.search_handler.search_text)
    search_layout.addWidget(window.search_btn)
    left_layout.addWidget(search_group)
    
    # Color picker
    window.color_picker = ColorPicker()
    left_layout.addWidget(window.color_picker)
    
    left_layout.addStretch()
    return left_panel

def create_right_panel(window):
    """Create the right panel with debug checkbox and log output."""
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    
    # Debug checkbox
    debug_layout = QHBoxLayout()
    window.debug_checkbox = QCheckBox("Enable Debug Logging")
    window.debug_checkbox.stateChanged.connect(window.toggle_debug)
    debug_layout.addWidget(window.debug_checkbox)
    debug_layout.addStretch()
    right_layout.addLayout(debug_layout)
    
    # Log output
    window.log_output = QTextEdit()
    window.log_output.setReadOnly(True)
    right_layout.addWidget(window.log_output)
    
    return right_panel