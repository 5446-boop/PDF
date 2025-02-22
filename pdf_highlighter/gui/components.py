"""GUI components for the PDF Highlighter application."""
import tkinter as tk
from tkinter import ttk, scrolledtext


class ConsoleOutput(scrolledtext.ScrolledText):
    """Scrolled text widget for console output."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(height=10, wrap=tk.WORD)
    
    def log(self, message):
        """Add a message to the console and scroll to the end."""
        self.insert(tk.END, message + "\n")
        self.yview(tk.END)


class MatchesTable(ttk.Treeview):
    """Treeview widget for displaying matches."""
    
    def __init__(self, parent):
        columns = ("Page Nr.", "Mat. No.", "File")
        super().__init__(parent, columns=columns, show="headings")
        
        for col in columns:
            self.heading(col, text=col)
        
        self.tag_configure("default", background="white")


class ControlPanel(tk.Frame):
    """Control panel containing buttons and inputs."""
    
    def __init__(self, parent, callbacks, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.setup_folder_controls(callbacks)
        self.setup_color_controls(callbacks)
        self.setup_text_input()
        self.setup_action_buttons(callbacks)
    
    def setup_folder_controls(self, callbacks):
        self.btn_folder = tk.Button(
            self, 
            text="Select Folder",
            command=callbacks["choose_folder"],
            bg="lightgreen"
        )
        self.btn_folder.pack(fill="x")
        
        self.folder_path_label = tk.Label(
            self,
            text="Folder Path",
            bg="lightgray",
            anchor="w"
        )
        self.folder_path_label.pack(fill="x", pady=5)
    
    def setup_color_controls(self, callbacks):
        self.btn_color = tk.Button(
            self,
            text="Select Highlight Color",
            command=callbacks["choose_color"],
            bg="lightgreen"
        )
        self.btn_color.pack(fill="x")
        
        self.color_label = tk.Label(
            self,
            text="Color Selected",
            bg="lightgray",
            anchor="w"
        )
        self.color_label.pack(fill="x", pady=5)
    
    def setup_text_input(self):
        self.text_label = tk.Label(
            self,
            text="Material Number:",
            bg="white"
        )
        self.text_label.pack(fill="x", pady=5)
        
        self.text_entry = tk.Entry(
            self,
            bg="lightyellow"
        )
        self.text_entry.pack(fill="x", pady=5)
    
    def setup_action_buttons(self, callbacks):
        self.btn_sound = tk.Button(
            self,
            text="Sound: ON",
            command=callbacks["toggle_sound"],
            bg="lightgreen"
        )
        self.btn_sound.pack(fill="x", pady=10)
        
        self.btn_process = tk.Button(
            self,
            text="PROCESS",
            command=callbacks["process_pdfs"],
            bg="lightgreen"
        )
        self.btn_process.pack(fill="x", pady=10)