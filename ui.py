import os
import sys
import fitz  # PyMuPDF
from PyQt5 import QtWidgets, QtGui, QtCore
from pdf_utils import rgb_to_hex
from pdf_processor import toggle_highlight_on_page, get_occurrence_annotation_color

class PDFViewer(QtWidgets.QGraphicsView):
    """
    Viser en PDF-side ved hjelp av en QGraphicsScene.
    """
    def __init__(self, parent=None):
        super(PDFViewer, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.pixmap_item = None
        self.doc = None         # Åpent dokument
        self.pdf_path = ""      # Nåværende PDF-filbane
        self.current_page = 0   # Nåværende side

    def load_pdf_page(self, pdf_path, page_number=0):
        """
        Laster PDF-filen og viser siden med indeks page_number.
        """
        try:
            doc = fitz.open(pdf_path)
            self.doc = doc
            self.pdf_path = pdf_path
            self.current_page = page_number
            page = doc.load_page(page_number)
            matrix = fitz.Matrix(2, 2)  # Øker oppløsningen
            pix = page.get_pixmap(matrix=matrix)
            image = QtGui.QImage(pix.samples, pix.width, pix.height, pix.stride, QtGui.QImage.Format_RGBA8888)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.scene.clear()
            self.pixmap_item = self.scene.addPixmap(pixmap)
            self.setSceneRect(self.scene.itemsBoundingRect())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Kunne ikke laste PDF-side: {e}")

    def refresh(self):
        """
        Oppdaterer visningen ved å laste gjeldende side på nytt.
        """
        if self.pdf_path and self.doc:
            self.load_pdf_page(self.pdf_path, self.current_page)

class MainWindow(QtWidgets.QWidget):
    """
    Hovedvindu med PDFViewer, kontrollpanel og resultat/logg-panel.
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("PDF Highlighter - PyQt")
        self.resize(1000, 800)
        
        # Variabler for PDF og annotasjonsfarge
        self.pdf_path = ""
        self.highlight_color = None  # Må velges av brukeren
        
        self.setup_ui()
    
    def setup_ui(self):
        # Hovedlayout med en vertikal splitter: øvre (PDF visning) og nedre (kontroll + resultater + logg)
        main_layout = QtWidgets.QVBoxLayout(self)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Øvre del: PDF visning
        viewer_widget = QtWidgets.QWidget()
        viewer_layout = QtWidgets.QVBoxLayout(viewer_widget)
        self.viewer = PDFViewer()
        viewer_layout.addWidget(self.viewer)
        splitter.addWidget(viewer_widget)
        
        # Nedre del: kontrollpanel, resultatpanel og logg
        lower_widget = QtWidgets.QWidget()
        lower_layout = QtWidgets.QVBoxLayout(lower_widget)
        splitter.addWidget(lower_widget)
        
        # Kontrollpanel
        control_panel = QtWidgets.QWidget()
        control_layout = QtWidgets.QHBoxLayout(control_panel)
        self.open_button = QtWidgets.QPushButton("Åpne PDF")
        self.open_button.clicked.connect(self.open_pdf)
        self.color_button = QtWidgets.QPushButton("Velg Highlight Farge")
        self.color_button.clicked.connect(self.choose_color)
        self.selected_color_label = QtWidgets.QLabel("Ingen farge valgt")
        self.selected_color_label.setAlignment(QtCore.Qt.AlignCenter)
        self.selected_color_label.setStyleSheet("background-color: none; padding: 5px;")
        self.keyword_edit = QtWidgets.QLineEdit()
        self.keyword_edit.setPlaceholderText("Skriv inn søkeord...")
        self.process_button = QtWidgets.QPushButton("Søk og oppdater liste")
        self.process_button.clicked.connect(self.process_pdfs)
        self.toggle_button = QtWidgets.QPushButton("Toggle Highlight")
        self.toggle_button.clicked.connect(self.toggle_highlight)
        
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.color_button)
        control_layout.addWidget(self.selected_color_label)
        control_layout.addWidget(self.keyword_edit)
        control_layout.addWidget(self.process_button)
        control_layout.addWidget(self.toggle_button)
        lower_layout.addWidget(control_panel)
        
        # Resultatpanel: viser en liste over funn
        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Side", "Søkeord", "Fil", "Highlight Farge"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.results_table.cellDoubleClicked.connect(self.on_result_double_click)
        lower_layout.addWidget(self.results_table)
        
        # Loggpanel
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        lower_layout.addWidget(self.log_text)
    
    def log(self, message: str):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def open_pdf(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Åpne PDF-fil", "", "PDF-filer (*.pdf)")
        if path:
            self.pdf_path = path
            self.viewer.load_pdf_page(path, page_number=0)
            self.log(f"Åpnet PDF: {path}")
    
    def choose_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.highlight_color = (color.redF(), color.greenF(), color.blueF())
            hex_color = rgb_to_hex(self.highlight_color)
            self.selected_color_label.setText(hex_color)
            self.selected_color_label.setStyleSheet(f"background-color: {hex_color}; padding: 5px;")
            self.log(f"Valgt farge: {hex_color}")
    
    def process_pdfs(self):
        """
        Søker på gjeldende side etter forekomster av søkeordet og oppdaterer resultatlisten.
        """
        if not self.pdf_path:
            self.log("Ingen PDF er åpnet.")
            return
        keyword = self.keyword_edit.text().strip()
        if not keyword:
            self.log("Skriv inn et søkeord.")
            return
        try:
            doc = self.viewer.doc
            if doc is None:
                self.log("PDF-dokumentet er ikke lastet.")
                return
            page = doc.load_page(self.viewer.current_page)
        except Exception as e:
            self.log(f"Feil ved lasting av side: {e}")
            return
        
        occurrences = page.search_for(keyword)
        self.results_table.setRowCount(0)
        if not occurrences:
            self.log("Ingen forekomster funnet på siden.")
            return
        
        # Sjekk om en annotasjon allerede finnes for forekomstene
        existing_color = get_occurrence_annotation_color(page, occurrences, threshold=0.1)
        row = 0
        self.results_table.setRowCount(1)
        self.results_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.viewer.current_page + 1)))
        self.results_table.setItem(row, 1, QtWidgets.QTableWidgetItem(keyword))
        self.results_table.setItem(row, 2, QtWidgets.QTableWidgetItem(self.pdf_path))
        color_str = rgb_to_hex(existing_color) if existing_color else "Ingen"
        self.results_table.setItem(row, 3, QtWidgets.QTableWidgetItem(color_str))
        self.log("Resultatlisten oppdatert.")
    
    def toggle_highlight(self):
        """
        Toggle annotasjoner på gjeldende side for det angitte søkeordet.
        Oppdaterer både PDF-visningen og resultatlisten.
        """
        if not self.pdf_path:
            self.log("Ingen PDF er åpnet.")
            return
        keyword = self.keyword_edit.text().strip()
        if not keyword:
            self.log("Skriv inn et søkeord.")
            return
        try:
            doc = self.viewer.doc
            if doc is None:
                self.log("PDF-dokumentet er ikke lastet.")
                return
            page = doc.load_page(self.viewer.current_page)
        except Exception as e:
            self.log(f"Feil ved lasting av side: {e}")
            return
        
        result = toggle_highlight_on_page(page, keyword, self.highlight_color, threshold=0.1)
        self.log(f"Toggle resultat: {result}")
        self.viewer.refresh()
        try:
            doc.save(self.pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            self.log("Endringer lagret i PDF.")
        except Exception as e:
            self.log(f"Feil ved lagring av PDF: {e}")
        self.process_pdfs()
    
    def on_result_double_click(self, row, column):
        self.toggle_highlight()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()