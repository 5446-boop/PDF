import os
import fitz  # PyMuPDF
import pygame
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, scrolledtext
from tkinter import ttk

# Spill av lyd dersom filen finnes
def play_sound(sound_file, sound_enabled):
    if sound_enabled and os.path.exists(sound_file):
        pygame.mixer.Sound(sound_file).play()

# Funksjon for å konvertere farge (tuple med 0-1 verdier) til hex-streng
def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

# Beregn arealet til et rektangel (fitz.Rect)
def rect_area(rect):
    return max(0, rect.x1 - rect.x0) * max(0, rect.y1 - rect.y0)

# Funksjon som beregner overlappingsareal mellom to rektangler
def intersection_area(rect1, rect2):
    inter = rect1.intersect(rect2)
    if inter is None:
        return 0
    return rect_area(inter)

# Sjekk om en forekomst (occ_rect) regnes som farget,
# dvs. om det finnes en highlight–annotasjon som overlapper med minst threshold av occ_rects areal.
def occurrence_is_highlighted(page, occ_rect, threshold=0.5):
    try:
        for annot in page.annots():
            if annot.type[0] == "Highlight":
                # Vi beregner andelen av forekomstens areal som overlapper annotasjonen.
                inter = occ_rect.intersect(annot.rect)
                if inter:
                    ratio = intersection_area(occ_rect, annot.rect) / rect_area(occ_rect)
                    if ratio >= threshold:
                        # Returner annotasjonens farge dersom den finnes
                        if annot.colors and "stroke" in annot.colors:
                            return annot.colors["stroke"]
    except Exception as e:
        pass  # Hvis ingen annotasjoner finnes, returner None
    return None

# Klassen for vårt program
class PDFHighlighterNew:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Highlighter – Ny tilnærming")
        self.root.geometry("800x600")
        pygame.mixer.init()

        # Globale variabler
        self.folder_path = ""
        self.highlight_color = None  # Brukeren må velge en farge før ny markering
        self.sound_enabled = True
        self.match_sound_file = "match_found_soft.wav"
        self.no_match_sound_file = "no_match_soft.wav"
        # Vi lagrer definerte tagger for Treeview i en ordbok
        self.defined_tags = {"default": {"bg": "white"}}
        # Terskel for at en forekomst skal anses som farget (andel overlapp)
        self.overlap_threshold = 0.5

        self.setup_ui()

    def setup_ui(self):
        # Hovedramme
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Topp-ramme (venstre kontroller, høyre Treeview)
        self.top_frame = tk.Frame(self.main_frame, padx=5, pady=5)
        self.top_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.top_frame, width=200, padx=10, pady=10, 
                                   highlightbackground="red", highlightthickness=2)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(self.top_frame, width=400, padx=10, pady=10, 
                                    highlightbackground="cyan", highlightthickness=2)
        self.right_frame.pack(side="left", fill="both", expand=True)

        # Bunn-ramme for konsoll/logg
        self.bottom_frame = tk.Frame(self.main_frame, height=200, padx=10, pady=10,
                                     highlightbackground="green", highlightthickness=2)
        self.bottom_frame.pack(fill="both", expand=True)

        # Venstre kontroller
        self.btn_folder = tk.Button(self.left_frame, text="Select Folder", command=self.choose_folder, bg="lightgreen")
        self.btn_folder.pack(fill="x")
        self.folder_path_label = tk.Label(self.left_frame, text="Folder Path", bg="lightgray", anchor="w")
        self.folder_path_label.pack(fill="x", pady=5)

        self.btn_color = tk.Button(self.left_frame, text="Select Highlight Color", command=self.choose_color, bg="lightgreen")
        self.btn_color.pack(fill="x")
        self.color_label = tk.Label(self.left_frame, text="Color Selected", bg="lightgray", anchor="w")
        self.color_label.pack(fill="x", pady=5)

        self.text_label = tk.Label(self.left_frame, text="Material Number:", bg="white")
        self.text_label.pack(fill="x", pady=5)
        self.text_entry = tk.Entry(self.left_frame, bg="lightyellow")
        self.text_entry.pack(fill="x", pady=5)

        self.btn_sound = tk.Button(self.left_frame, text="Sound: ON", command=self.toggle_sound, bg="lightgreen")
        self.btn_sound.pack(fill="x", pady=10)

        self.btn_process = tk.Button(self.left_frame, text="PROCESS", command=self.process_pdfs, bg="lightgreen")
        self.btn_process.pack(fill="x", pady=10)

        # Høyre – Treeview for resultater
        columns = ("Page Nr.", "Mat. No.", "File")
        self.matches_list_table = ttk.Treeview(self.right_frame, columns=columns, show="headings")
        self.matches_list_table.heading("Page Nr.", text="Page Nr.")
        self.matches_list_table.heading("Mat. No.", text="Mat. No.")
        self.matches_list_table.heading("File", text="File")
        self.matches_list_table.pack(fill="both", expand=True)
        self.matches_list_table.tag_configure("default", background="white")
        self.matches_list_table.bind("<Double-1>", self.on_row_double_click)

        # Bunn – konsoll/logg
        self.console_output = scrolledtext.ScrolledText(self.bottom_frame, height=10, wrap=tk.WORD)
        self.console_output.pack(fill="both", expand=True)
        self.log("Console output will appear here...")

    def log(self, message):
        self.console_output.insert(tk.END, message + "\n")
        self.console_output.yview(tk.END)

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.btn_sound.config(text="Sound: ON", bg="lightgreen")
        else:
            self.btn_sound.config(text="Sound: OFF", bg="red")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.folder_path_label.config(text=folder)

    def choose_color(self):
        rgb_color, hex_color = colorchooser.askcolor(title="Choose Highlight Color")
        if rgb_color:
            self.highlight_color = (rgb_color[0]/255, rgb_color[1]/255, rgb_color[2]/255)
            self.color_label.config(bg=hex_color)

    def process_pdfs(self):
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder.")
            return

        keyword = self.text_entry.get().strip()
        if not keyword:
            messagebox.showerror("Error", "Please enter a Material Number (Mat. No.).")
            return

        self.log(f"Searching for '{keyword}'...")
        self.matches_list_table.delete(*self.matches_list_table.get_children())
        inserted_entries = set()  # For å unngå duplikater: (filename, page_index)
        found_match = False

        # Gå gjennom alle PDF-filer i mappen
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(self.folder_path, filename)
                try:
                    doc = fitz.open(pdf_path)
                except Exception as e:
                    self.log(f"Error opening {filename}: {e}")
                    continue

                for page_index in range(len(doc)):
                    page = doc[page_index]
                    occurrences = page.search_for(keyword)
                    if occurrences:
                        # For hver forekomst, sjekk om den er farget
                        existing_color = None
                        for occ in occurrences:
                            existing_color = occurrence_is_highlighted(page, occ, threshold=self.overlap_threshold)
                            if existing_color is not None:
                                break
                        key = (filename, page_index)
                        if key not in inserted_entries:
                            inserted_entries.add(key)
                            display_page = page_index + 1
                            if existing_color is not None:
                                hex_color = rgb_to_hex(existing_color)
                                tag_name = f"bg_{hex_color}"
                                if tag_name not in self.defined_tags:
                                    self.matches_list_table.tag_configure(tag_name, background=hex_color)
                                    self.defined_tags[tag_name] = {"bg": hex_color}
                                self.matches_list_table.insert("", "end", values=(display_page, keyword, filename), tags=(tag_name,))
                            else:
                                self.matches_list_table.insert("", "end", values=(display_page, keyword, filename))
                            found_match = True
                doc.close()

        if not found_match:
            self.log("No matches found.")
            play_sound(self.no_match_sound_file, self.sound_enabled)
        else:
            play_sound(self.match_sound_file, self.sound_enabled)
        self.log("Processing complete.")

    def on_row_double_click(self, event):
        selected = self.matches_list_table.focus()
        if not selected:
            return
        values = self.matches_list_table.item(selected, "values")
        if len(values) < 3:
            self.log("Invalid row selection.")
            return
        page_num_str, keyword, filename = values
        try:
            page_index = int(page_num_str) - 1
        except Exception as e:
            self.log("Error parsing page number: " + str(e))
            return
        pdf_path = os.path.join(self.folder_path, filename)
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            self.log(f"Error opening {filename}: {e}")
            return
        if page_index >= len(doc):
            self.log(f"Page {page_num_str} does not exist in {filename}.")
            doc.close()
            return
        page = doc[page_index]
        result = self.toggle_highlight_on_page(page, keyword)
        if result == "no_color":
            self.log("Please select a highlight color before adding a highlight.")
        elif result == "added":
            self.log(f"Added highlight for '{keyword}' on page {page_num_str} in file '{filename}'")
            tag_name = f"bg_{rgb_to_hex(self.highlight_color)}"
            if tag_name not in self.defined_tags:
                self.matches_list_table.tag_configure(tag_name, background=rgb_to_hex(self.highlight_color))
                self.defined_tags[tag_name] = {"bg": rgb_to_hex(self.highlight_color)}
            self.matches_list_table.item(selected, tags=(tag_name,))
        elif result == "removed":
            self.log(f"Removed highlight for '{keyword}' on page {page_num_str} in file '{filename}'")
            self.matches_list_table.item(selected, tags=("default",))
        try:
            doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        except Exception as e:
            self.log(f"Error saving {filename}: {e}")
        doc.close()

    def toggle_highlight_on_page(self, page, keyword):
        occurrences = page.search_for(keyword)
        if not occurrences:
            return None
        # Sjekk om minst én forekomst er farget
        already_highlighted = False
        for occ in occurrences:
            if occurrence_is_highlighted(page, occ, threshold=self.overlap_threshold) is not None:
                already_highlighted = True
                break
        if already_highlighted:
            # Fjern alle annotasjoner som overlapper med forekomstene
            try:
                for annot in list(page.annots() or []):
                    if annot.type[0] == "Highlight":
                        for occ in occurrences:
                            # Vi fjerner annotasjonen hvis den overlapper i en betydelig andel
                            ratio = intersection_area(occ, annot.rect) / rect_area(occ)
                            if ratio >= self.overlap_threshold:
                                annot.delete()
                                break
            except Exception as e:
                self.log("Error removing annotations: " + str(e))
            return "removed"
        else:
            if self.highlight_color is None:
                return "no_color"
            try:
                for occ in occurrences:
                    annot = page.add_highlight_annot(occ)
                    annot.set_colors(stroke=self.highlight_color)
                    annot.update()
            except Exception as e:
                self.log("Error adding annotations: " + str(e))
            return "added"

    def run(self):
        self.root.mainloop()

# Bruk funksjonen occurrence_is_highlighted definert utenfor klassen
def occurrence_is_highlighted(page, occ_rect, threshold=0.5):
    try:
        for annot in page.annots():
            if annot.type[0] == "Highlight":
                inter = occ_rect.intersect(annot.rect)
                if inter:
                    ratio = intersection_area(occ_rect, annot.rect) / rect_area(occ_rect)
                    if ratio >= threshold:
                        if annot.colors and "stroke" in annot.colors:
                            return annot.colors["stroke"]
    except Exception as e:
        pass
    return None

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFHighlighterNew(root)
    app.run()
