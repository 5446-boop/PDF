"""
PDF Highlighter 2.0 - Main Window
Hovedvinduet med PDF-visning og kontroller.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QTextEdit, QFileDialog,
    QMessageBox, QColorDialog
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor

from ..core.pdf_utils import rgb_to_hex
from ..config.settings import AppConfig
from .viewer import PDFViewer
from .shortcuts import Shortcuts

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_path = ""
        self.highlight_color = None
        
        # UI oppsett
        self.setup_ui()
        self.setup_shortcuts()
        
        # Sett vindutittel og størrelse
        self.setWindowTitle(f"{AppConfig.APP_NAME} {AppConfig.VERSION}")
        self.resize(AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT)
        
    def setup_ui(self):
        # Hovedlayout
        main_layout = QVBoxLayout(self)
        
        # Verktøylinje på toppen
        toolbar = self.create_toolbar()
        main_layout.addLayout(toolbar)
        
        # Splitter for PDF-visning og resultatpanel
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # PDF-visning
        self.viewer = PDFViewer(self)
        splitter.addWidget(self.viewer)
        
        # Nedre panel (søk og resultater)
        bottom_panel = self.create_bottom_panel()
        splitter.addWidget(bottom_panel)
        
        # Sett splitter-størrelser
        splitter.setSizes([700, 300])  # 70% topp, 30% bunn
        
    def create_toolbar(self):
        toolbar = QHBoxLayout()
        
        # Fil-knapp med meny
        self.open_button = QPushButton("Åpne PDF")
        self.open_button.clicked.connect(self.open_pdf)
        toolbar.addWidget(self.open_button)
        
        # Navigasjonsknapper
        self.prev_page_btn = QPushButton("←")
        self.prev_page_btn.setToolTip("Forrige side")
        self.prev_page_btn.clicked.connect(self.viewer.previous_page)
        
        self.next_page_btn = QPushButton("→")
        self.next_page_btn.setToolTip("Neste side")
        self.next_page_btn.clicked.connect(self.viewer.next_page)
        
        self.page_label = QLabel("Side: 0 / 0")
        
        toolbar.addWidget(self.prev_page_btn)
        toolbar.addWidget(self.page_label)
        toolbar.addWidget(self.next_page_btn)
        
        # Zoom-kontroller
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setToolTip("Zoom ut")
        self.zoom_out_btn.clicked.connect(self.viewer.zoom_out)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom inn")
        self.zoom_in_btn.clicked.connect(self.viewer.zoom_in)
        
        self.zoom_label = QLabel("100%")
        
        toolbar.addWidget(self.zoom_out_btn)
        toolbar.addWidget(self.zoom_label)
        toolbar.addWidget(self.zoom_in_btn)
        
        # Highlight-kontroller
        self.color_button = QPushButton("Velg farge")
        self.color_button.clicked.connect(self.choose_color)
        
        self.selected_color_label = QLabel("Ingen farge valgt")
        self.selected_color_label.setStyleSheet("padding: 5px;")
        
        toolbar.addWidget(self.color_button)
        toolbar.addWidget(self.selected_color_label)
        
        toolbar.addStretch()  # Fyller resten av plassen
        return toolbar
        
    def create_bottom_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Søkepanel
        search_layout = QHBoxLayout()
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("Skriv inn søkeord...")
        self.search_button = QPushButton("Søk")
        self.search_button.clicked.connect(self.search_text)
        
        search_layout.addWidget(self.keyword_edit)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Resultattabell
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Side", "Søkeord", "Kontekst", "Status"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
        # Logg
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        layout.addWidget(self.log_text)
        
        return panel
        
    def setup_shortcuts(self):
        # Fil-operasjoner
        self.create_shortcut(Shortcuts.OPEN_FILE, self.open_pdf)
        self.create_shortcut(Shortcuts.SAVE_FILE, self.save_pdf)
        
        # Navigasjon
        self.create_shortcut(Shortcuts.NEXT_PAGE, self.viewer.next_page)
        self.create_shortcut(Shortcuts.PREV_PAGE, self.viewer.previous_page)
        
        # Zoom
        self.create_shortcut(Shortcuts.ZOOM_IN, self.viewer.zoom_in)
        self.create_shortcut(Shortcuts.ZOOM_OUT, self.viewer.zoom_out)
        
    def create_shortcut(self, key_sequence, slot):
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.activated.connect(slot)
        
    @pyqtSlot()
    def open_pdf(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Åpne PDF-fil",
            "",
            "PDF-filer (*.pdf)"
        )
        if path:
            self.pdf_path = path
            self.viewer.load_pdf(path)
            self.update_page_label()
            self.log(f"Åpnet PDF: {path}")
            
    @pyqtSlot()
    def save_pdf(self):
        if self.pdf_path:
            try:
                self.viewer.save_pdf()
                self.log("PDF lagret")
            except Exception as e:
                self.log(f"Feil ved lagring: {e}")
                QMessageBox.critical(self, "Feil", f"Kunne ikke lagre PDF: {e}")
                
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.highlight_color = (
                color.redF(),
                color.greenF(),
                color.blueF()
            )
            hex_color = rgb_to_hex(self.highlight_color)
            self.selected_color_label.setText(hex_color)
            self.selected_color_label.setStyleSheet(
                f"background-color: {hex_color}; padding: 5px;"
            )
            self.log(f"Valgt farge: {hex_color}")
            
    @pyqtSlot()
    def search_text(self):
        keyword = self.keyword_edit.text().strip()
        if not keyword:
            self.log("Skriv inn et søkeord")
            return
            
        if not self.pdf_path:
            self.log("Ingen PDF er åpnet")
            return
            
        results = self.viewer.search_text(keyword)
        self.update_results_table(results)
        
    def update_results_table(self, results):
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.results_table.setItem(
                row, 0, QTableWidgetItem(str(result['page'] + 1))
            )
            self.results_table.setItem(
                row, 1, QTableWidgetItem(result['keyword'])
            )
            self.results_table.setItem(
                row, 2, QTableWidgetItem(result['context'])
            )
            self.results_table.setItem(
                row, 3, QTableWidgetItem(result['status'])
            )
            
    def update_page_label(self):
        current = self.viewer.current_page + 1
        total = self.viewer.total_pages
        self.page_label.setText(f"Side: {current} / {total}")
        
    def update_zoom_label(self):
        zoom = int(self.viewer.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom}%")
        
    def log(self, message: str):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )