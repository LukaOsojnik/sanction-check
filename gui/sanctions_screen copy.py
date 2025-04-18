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
        
        # Create the frame for this screen
        self.frame = ttk.Frame(root)
        
        # Build the UI components
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up all UI components for the sanctions screen"""
        # Add a back button to return to welcome page
        self.back_button = ttk.Button(
            self.frame,
            text="⬅️ Natrag",
            command=self.on_back_callback
        )
        self.back_button.place(x=10, y=10)

        # Create a frame for the table
        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(padx=10, pady=(40, 10), fill="both", expand=True)
        
        # Create the Treeview widget (table)
        self.columns = ("ime", "prezime", "oib", "adresa")
        self.table = ttk.Treeview(self.table_frame, columns=self.columns, show="headings")
        
        # Define the column headings
        self.table.heading("ime", text="Ime i prezime")
        self.table.heading("prezime", text="Prezime")
        self.table.heading("oib", text="OIB/ID broj")
        self.table.heading("adresa", text="Adresa")
        
        # Set column widths
        self.table.column("ime", width=150)
        self.table.column("prezime", width=150)
        self.table.column("oib", width=100)
        self.table.column("adresa", width=150)
        
        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)
        
        # Add progress bar frame at the bottom
        self.progress_frame = ttk.Frame(self.frame)
        self.progress_frame.pack(fill="x", padx=10, pady=10)
        
        # Status label
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.pack(side="top", anchor="w")
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=780,
            mode="determinate"
        )
        self.progress_bar.pack(side="bottom", fill="x")
        
        # Configure row colors
        self.table.tag_configure("sanction", background="#ffcccc")
    
    def add_person_object(self, person):
        """Add a Person object to the table and color based on matching sanctions"""
        table_id = self.table.insert("", "end", values=(
            person.name,
            person.oib,
            person.address
        ))
        # Apply red color to all sanction-matched rows
        self.table.item(table_id, tags=("sanction",))
        return table_id
    
    def update_progress(self, current, total):
        """Update the progress bar based on current progress"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar["value"] = percentage
            self.root.update_idletasks()  # Force update of the UI
    
    def update_status(self, message):
        """Update the status label with a new message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()  # Force update of the UI
    
    def reset_progress(self):
        """Reset progress bar to zero"""
        self.progress_bar["value"] = 0
        self.status_label.config(text="Ready")
        self.root.update_idletasks()
    
    def clear_table(self):
        """Clear all items from the table"""
        for item in self.table.get_children():
            self.table.delete(item)
    
    def show(self):
        """Display this screen and reset UI elements"""
        self.reset_progress()
        self.clear_table()
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Hide this screen"""
        self.frame.pack_forget()