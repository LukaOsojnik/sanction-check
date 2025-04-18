"""
Welcome screen module for the sanctions checking application.
"""
import tkinter as tk
from tkinter import ttk, filedialog
import os
from typing import Callable

from interfaces import IWelcomeScreen
from config import AppConfig

class WelcomeScreen(IWelcomeScreen):
    def __init__(self, root: tk.Tk, on_start_callback: Callable, on_file_drop_callback: Callable):
   
        self.root = root
        self.on_start_callback = on_start_callback
        self.on_file_drop_callback = on_file_drop_callback
    
        self.frame = ttk.Frame(root)
        
        # UI 
        self._setup_ui()
    
    def _setup_ui(self):
     
        title_label = ttk.Label(
            self.frame, 
            text="Dobrodošli u aplikaciju za provjeru sankcioniranih osoba", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(40, 20))
        
        # File selection area
        self.file_frame = ttk.LabelFrame(
            self.frame,
            text="Učitaj listu klijenata",
            width=500,
            height=160
        )
        self.file_frame.pack(pady=20, padx=50, fill="x")
    
        self.file_frame.pack_propagate(False)
        
        # Selection button
        self.file_button = ttk.Button(
            self.file_frame,
            text="Odaberi CSV ili Excel datoteku",
            command=self._open_file_dialog,
            width=25
        )
        self.file_button.pack(pady=20)
        
        self.file_path_label = ttk.Label(
            self.file_frame,
            text="Nije odabrana datoteka",
            font=("Arial", 9),
            foreground="gray"
        )
        self.file_path_label.pack(pady=5)
        
        self.file_status_label = ttk.Label(
            self.frame,
            text="Nije učitana datoteka s klijentima",
            font=("Arial", 10),
            foreground="gray"
        )
        self.file_status_label.pack(pady=5)
        
        # Status label za prikaz statusa preuzimanja
        self.status_label = ttk.Label(
            self.frame,
            text="Inicijalizacija...",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
        
        # Button to start the process
        self.start_button = ttk.Button(
            self.frame,
            text="Pokreni provjeru",
            command=self.on_start_callback,
            width=20,
            state="disabled" # inicijalno iskljuceno
        )
        self.start_button.pack(pady=15)
        
        version_label = ttk.Label(
            self.frame,
            text=f"Verzija {AppConfig.VERSION}",
            font=("Arial", 8)
        )
        version_label.pack(side="bottom", pady=10)
    
    def _open_file_dialog(self):
     
        file_path = filedialog.askopenfilename(
            title="Odaberi datoteku s klijentima",
            filetypes=[
                ("CSV datoteke", "*.csv"),
                ("Excel datoteke", "*.xlsx *.xls"),
                ("Sve datoteke", "*.*")
            ]
        )
        
        if file_path:
        
            file_name = os.path.basename(file_path)
            self.file_path_label.config(
                text=f"Odabrana datoteka: {file_name}",
                foreground="blue"
            )
            
            self.on_file_drop_callback(file_path)
    
    def update_file_status(self, message: str, is_success: bool = True):
    
        self.file_status_label.config(
            text=message,
            foreground="green" if is_success else "red"
        )
        
        self.start_button.config(state="normal" if is_success else "disabled")
    
    def update_status(self, message: str):
      
        self.status_label.config(text=message)
        self.root.update_idletasks()  
    
    def show(self):
   
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):

        self.frame.pack_forget()
