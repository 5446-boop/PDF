"""Main application module for PDF Highlighter."""
import os
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import pygame
import fitz

from pdf_highlighter.utils import (
    play_sound,
    rgb_to_hex,
    occurrence_is_highlighted,
    intersection_area,
    rect_area
)
from pdf_highlighter.gui.components import (
    ConsoleOutput,
    MatchesTable,
    ControlPanel
)


class PDFHighlighter:
    """Main application class for PDF Highlighter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Highlighter")
        self.root.geometry("800x600")
        pygame.mixer.init()

        # Initialize variables
        self.folder_path = ""
        self.highlight_color = None
        self.sound_enabled = True
        self.match_sound_file = "resources/match_found_soft.wav"
        self.no_match_sound_file = "resources/no_match_soft.wav"
        self.defined_tags = {"default": {"bg": "white"}}
        self.overlap_threshold = 0.5

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Top frame
        self.top_frame = tk.Frame(self.main_frame, padx=5, pady=5)
        self.top_frame.pack(fill="both", expand=True)

        # Control panel (left side)
        self.control_panel = ControlPanel(
            self.top_frame,
            callbacks={
                "choose_folder": self.choose_folder,
                "choose_color": self.choose_color,
                "toggle_sound": self.toggle_sound,
                "process_pdfs": self.process_pdfs
            },
            width=200,
            padx=10,
            pady=10,
            highlightbackground="red",
            highlightthickness=2
        )
        self.control_panel.pack(side="left", fill="y")

        # Results panel (right side)
        self.right_frame = tk.Frame(
            self.top_frame,
            width=400,
            padx=10,
            pady=10,
            highlightbackground="cyan",
            highlightthickness=2
        )
        self.right_frame.pack(side="left", fill="both", expand=True)

        # Matches table
        self.matches_list_table = MatchesTable(self.right_frame)
        self.matches_list_table.pack(fill="both", expand=True)
        self.matches_list_table.bind("<Double-1>", self.on_row_double_click)

        # Console output
        self.bottom_frame = tk.Frame(
            self.main_frame,
            height=200,
            padx=10,
            pady=10,
            highlightbackground="green",
            highlightthickness=2
        )
        self.bottom_frame.pack(fill="both", expand=True)

        self.console_output = ConsoleOutput(self.bottom_frame)
        self.console_output.pack(fill="both", expand=True)
        self.console_output.log("Console output will appear here...")

    def toggle_sound(self):
        """Toggle sound on/off."""
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.control_panel.btn_sound.config(text="Sound: ON", bg="lightgreen")
        else:
            self.control_panel.btn_sound.config(text="Sound: OFF", bg="red")

    def choose_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.control_panel.folder_path_label.config(text=folder)

    def choose_color(self):
        """Open color selection dialog."""
        rgb_color, hex_color = colorchooser.askcolor(title="Choose Highlight Color")
        if rgb_color:
            self.highlight_color = (rgb_color[0]/255, rgb_color[1]/255, rgb_color[2]/255)
            self.control_panel.color_label.config(bg=hex_color)

    def process_pdfs(self):
        """Process PDF files in the selected folder."""
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a folder.")
            return

        keyword = self.control_panel.text_entry.get().strip()
        if not keyword:
            messagebox.showerror("Error", "Please enter a Material Number (Mat. No.).")
            return

        self.console_output.log(f"Searching for '{keyword}'...")
        self.matches_list_table.delete(*self.matches_list_table.get_children())
        inserted_entries = set()
        found_match = False

        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(".pdf"):
                self._process_pdf_file(filename, keyword, inserted_entries)
                found_match = True

        if not found_match:
            self.console_output.log("No matches found.")
            play_sound(self.no_match_sound_file, self.sound_enabled)
        else:
            play_sound(self.match_sound_file, self.sound_enabled)
        self.console_output.log("Processing complete.")

    def _process_pdf_file(self, filename, keyword, inserted_entries):
        """Process a single PDF file."""
        pdf_path = os.path.join(self.folder_path, filename)
        try:
            doc = fitz.open(pdf_path)
            for page_index in range(len(doc)):
                self._process_page(doc, page_index, keyword, filename, inserted_entries)
            doc.close()
        except Exception as e:
            self.console_output.log(f"Error processing {filename}: {e}")

    def _process_page(self, doc, page_index, keyword, filename, inserted_entries):
        """Process a single page in a PDF file."""
        page = doc[page_index]
        occurrences = page.search_for(keyword)
        if occurrences:
            existing_color = None
            for occ in occurrences:
                existing_color = occurrence_is_highlighted(
                    page, occ, threshold=self.overlap_threshold
                )
                if existing_color is not None:
                    break

            key = (filename, page_index)
            if key not in inserted_entries:
                inserted_entries.add(key)
                self._add_match_to_table(
                    page_index + 1, keyword, filename, existing_color
                )

    def _add_match_to_table(self, page_num, keyword, filename, existing_color):
        """Add a match to the results table."""
        if existing_color is not None:
            hex_color = rgb_to_hex(existing_color)
            tag_name = f"bg_{hex_color}"
            if tag_name not in self.defined_tags:
                self.matches_list_table.tag_configure(tag_name, background=hex_color)
                self.defined_tags[tag_name] = {"bg": hex_color}
            self.matches_list_table.insert(
                "", "end",
                values=(page_num, keyword, filename),
                tags=(tag_name,)
            )
        else:
            self.matches_list_table.insert(
                "",