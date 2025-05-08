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

        self.person_objects = {}  

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

        self.table.bind("<<TreeviewSelect>>", self._on_table_select)

        # Gumb za proširivanje
        self.expand_button = ttk.Button(
            self.table_frame,
            text="Proširi",
            command=self._show_matching_names,
            state="disabled"  # inicijalno isključeno
        )
        self.expand_button.pack(side="top", anchor="w", pady=(5, 0))

        # Okvir za dodatnu tablicu
        self.details_frame = ttk.LabelFrame(self.frame, text="Podudarajuća imena")

        # Dodatna tablica
        self.details_table = ttk.Treeview(self.details_frame, columns=("matching_name"), show="headings")
        self.details_table.heading("matching_name", text="Ime na listi sankcija")
        self.details_table.column("matching_name", width=300)

        # Scrollbar za dodatnu tablicu
        self.details_scrollbar = ttk.Scrollbar(self.details_frame, orient=tk.VERTICAL, command=self.details_table.yview)
        self.details_table.configure(yscroll=self.details_scrollbar.set)
        self.details_scrollbar.pack(side="right", fill="y")
        self.details_table.pack(fill="both", expand=True)

    def _on_table_select(self, event):

        selected_items = self.table.selection()
        self.expand_button.config(state="normal" if selected_items else "disabled")

    def _show_matching_names(self):
    
        for item in self.details_table.get_children():
            self.details_table.delete(item)
        
        selected_items = self.table.selection()
        if not selected_items:
            return
        
      
        selected_id = selected_items[0]
        person_obj = self.person_objects.get(selected_id)
        
        if person_obj and hasattr(person_obj, "matching_names") and person_obj.matching_names:
          
            for name in person_obj.matching_names:
                self.details_table.insert("", "end", values=(name,))
        
            self.details_frame.pack(padx=10, pady=(5, 10), fill="both", expand=True)
        else:
           
            self.details_frame.pack_forget()    

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
         
                self.root.after(500, self._open_link, None)
    
    def add_person_object(self, person):
        """
        Add a person to the results table
        
        Parameters:
        person - Person object to add
        """
        table_id = self.table.insert("", "end", values=(
            person.name,
            person.oib,
            person.address
        ))

        self.table.item(table_id, tags=("sanction",))
        self.person_objects[table_id] = person 
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
        """Clear all entries from the results table"""
        for item in self.table.get_children():
            self.table.delete(item)
        self.person_objects.clear() 
     
        self.details_frame.pack_forget()
    
    def show(self):
       
        self.reset_progress()
        self.clear_table()
        self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Hide this screen"""
        self.details_frame.pack_forget()  
        self.frame.pack_forget()