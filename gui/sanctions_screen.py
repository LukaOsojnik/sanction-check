"""
Main sanctions check screen module for the application.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

class SanctionsScreen:
    def __init__(self, root, on_back_callback):
        """
        Initialize the sanctions check screen
        
        Parameters:
        root - The Tkinter root or parent frame
        on_back_callback - Function to call when the back button is clicked
        """
        self.root = root
        self.on_back_callback = on_back_callback
        
        # frame
        self.frame = ttk.Frame(root)
        
        # create ui
        self._setup_ui()
    
    def _setup_ui(self):
        
        # back button 
        self.back_button = ttk.Button(
            self.frame,
            text="⬅️ Natrag",
            command=self.on_back_callback
        )
        self.back_button.place(x=10, y=10)

        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(padx=10, pady=(40, 10), fill="both", expand=True)
        
        self.columns = ("ime", "oib", "adresa")
        self.table = ttk.Treeview(self.table_frame, columns=self.columns, show="headings")
        
        self.table.heading("ime", text="Ime i prezime")
        self.table.heading("oib", text="OIB/ID broj")
        self.table.heading("adresa", text="Adresa")

        self.table.column("ime", width=150)
        self.table.column("oib", width=100)
        self.table.column("adresa", width=150)

        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)

        self.progress_frame = ttk.Frame(self.frame)
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        

        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.pack(side="top", anchor="w")
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=780,
            mode="determinate"
        )
        self.progress_bar.pack(side="bottom", fill="x")
        
        self.table.tag_configure("sanction", background="#ffcccc")
    
    def add_person_object(self, person):
        
        table_id = self.table.insert("", "end", values=(
            person.name,
            person.oib,
            person.address
        ))
        
        self.table.item(table_id, tags=("sanction",))
        return table_id
    
    def update_progress(self, current, total):
    
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar["value"] = percentage
            self.root.update_idletasks() 
    
    def update_status(self, message):

        self.status_label.config(text=message)
        self.root.update_idletasks()  
    
    def reset_progress(self):
    
        self.progress_bar["value"] = 0
        self.status_label.config(text="Ready")
        self.root.update_idletasks()
    
    def clear_table(self):
       
        for item in self.table.get_children():
            self.table.delete(item)
    
    def show(self):
      
        self.reset_progress()
        self.clear_table()
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
    
        self.frame.pack_forget()