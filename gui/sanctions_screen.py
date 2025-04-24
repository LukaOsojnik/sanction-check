"""
Main sanctions check screen module for the application.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
import webbrowser

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
        
        self.frame = ttk.Frame(root)
        
        self._setup_ui()
    
    def _setup_ui(self):
        
        # Create a top navigation frame
        self.nav_frame = ttk.Frame(self.frame)
        self.nav_frame.pack(fill="x", padx=10, pady=10, anchor="nw")
        
        # Back button
        self.back_button = ttk.Button(
            self.nav_frame,
            text="⬅️ Natrag",
            command=self.on_back_callback
        )
        self.back_button.pack(side="left")

        # MVEP link 
        self.link_label = ttk.Label(
            self.nav_frame,
            text="MVEP tražilica",
            foreground="blue",
            cursor="hand2"
        )
        self.link_label.pack(side="right", padx=(0, 50))
       
        font = tkfont.Font(self.link_label, self.link_label.cget("font"))
        font.configure(underline=True)
        self.link_label.configure(font=font)
        
        self.link_label.bind("<Button-1>", self._open_link)
        
        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(padx=10, pady=(10, 10), fill="both", expand=True)
        
        self.columns = ("ime i prezime", "oib", "adresa")
        self.table = ttk.Treeview(self.table_frame, columns=self.columns, show="headings")
        
        self.table.heading("ime i prezime", text="Ime i prezime")
        self.table.heading("oib", text="OIB")
        self.table.heading("adresa", text="Adresa")
        
        self.table.column("ime i prezime", width=150)
        self.table.column("oib", width=150)
        self.table.column("adresa", width=100)
        
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)
        
        self.table.bind("<Double-1>", self._copy_name_surname)
        
        self.tooltip_label = ttk.Label(
            self.table_frame, 
            text="Double-click for copy to clipboard",
            font=("", 9, "italic")
        )
        self.tooltip_label.pack(anchor="w", pady=(5, 0))
        
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
    
    def _open_link(self, event):
      
        webbrowser.open("https://mvep.gov.hr/vanjska-politika/mjere-ogranicavanja/eu-i-un-konsolidirani-popisi-mjera-ogranicavanja/272447")
    
    def _copy_name_surname(self, event):
   
        item_id = self.table.identify_row(event.y)
        if item_id: 
            row_values = self.table.item(item_id, "values")
            if len(row_values) >= 2:
                name_surname = f"{row_values[0]}"
                self.root.clipboard_clear()
                self.root.clipboard_append(name_surname)
                self.update_status(f"Copied to clipboard: {name_surname}")
                # Add delay before opening link
                self.root.after(500, self._open_link, None)  # 500ms delay
    
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