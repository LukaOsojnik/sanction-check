import os
import sys
from datetime import datetime
import subprocess
from tkinter import filedialog, messagebox

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFExporter:
   
    def __init__(self, parent_window):
        """
        Parameters:
        parent_window - The parent window for showing dialogs
        """
        self.parent = parent_window
        
    def export_to_pdf(self, people_objects, status_update_callback=None):
        """
        Export the results to a PDF file
        
        Parameters:
        people_objects - Dictionary of person objects to include in the report
        status_update_callback - Optional callback for updating status messages
        
        Returns:
        bool - True if export was successful, False otherwise
        """
        # check if results exist
        if not people_objects:
            messagebox.showinfo("Nema rezultata za PDF.")
            return False
        
        # save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF datoteke", "*.pdf"), ("Sve datoteke", "*.*")],
            title="Spremi PDF izvještaj"
        )
        
        if not file_path:
            return False
        
        # generate PDF
        try:
            if status_update_callback:
                status_update_callback("Generiranje PDF izvještaja...")
                
            self._generate_pdf(file_path, people_objects)
            
            if status_update_callback:
                status_update_callback(f"PDF izvještaj spremljen: {file_path}")
            
            # ask if user wants to open the file
            if messagebox.askyesno("Izvoz PDF", "PDF izvještaj je uspješno generiran. Želite li ga otvoriti?"):
                # open pdf
                if sys.platform == 'win32':
                    os.startfile(file_path)
                else:  # za linux
                    subprocess.run(['xdg-open' if sys.platform.startswith('linux') else 'open', file_path])
            
            return True
                    
        except Exception as e:
            messagebox.showerror("Greška", f"Greška pri generiranju PDF-a: {str(e)}")
            if status_update_callback:
                status_update_callback("Greška pri generiranju PDF-a")
            return False

    def _generate_pdf(self, file_path, people_objects):
        """
        Generate a PDF with the results
        
        Parameters:
        file_path - Path where to save the PDF file
        people_objects - Dictionary of person objects to include in the report
        """
        # finding font that supports Croatian characters
        try:
            # windows
            if sys.platform == 'win32':
                font_path = "C:/Windows/Fonts/Arial.ttf"
            else:  # linux
                font_path = "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf"
                
            if font_path and os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                base_font = 'CustomFont'
            else:
                base_font = 'Helvetica'
        except:
            base_font = 'Helvetica'
        
        # create PDF document
        doc = SimpleDocTemplate(
            file_path, pagesize=A4, 
            rightMargin=2*cm, leftMargin=2*cm, 
            topMargin=2*cm, bottomMargin=2*cm
        )
        
        # story and styles
        story = []
        styles = getSampleStyleSheet()
        
        # define styles
        title_style = ParagraphStyle(
            'Title', parent=styles['Heading1'],
            fontName=base_font, fontSize=18, alignment=1
        )
        normal_style = ParagraphStyle(
            'Normal', parent=styles['Normal'],
            fontName=base_font, fontSize=10
        )
        
        # add title and date
        story.append(Paragraph("Izvještaj o provjeri sankcioniranih osoba", title_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"Datum izvještaja: {datetime.now().strftime('%d.%m.%Y. %H:%M')}", normal_style))
        story.append(Spacer(1, 1*cm))
        
        # helper function
        def create_styled_table(data, col_widths, header=True):
            table = Table(data, colWidths=col_widths)
            styles_list = [
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, -1), base_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            if header:
                styles_list.extend([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                ])
                
            table.setStyle(TableStyle(styles_list))
            return table
        
        # main table
        main_data = [["Ime", "Prezime", "OIB", "Adresa", "Podudaranja"]]
        matched_persons = []
        
        for item_id, person in people_objects.items():
            main_data.append([
                person.name, person.surname, person.oib, 
                person.address, str(person.count)
            ])
            
            if hasattr(person, "matching_names") and person.matching_names:
                matched_persons.append(person)
        
        story.append(create_styled_table(main_data, [3*cm, 3*cm, 3*cm, 5*cm, 3*cm]))
        story.append(Spacer(1, 1*cm))
        
        # matching details
        if matched_persons:
            story.append(Paragraph("Detalji podudaranja", title_style))
            story.append(Spacer(1, 0.5*cm))
            
            for person in matched_persons:
                story.append(Paragraph(f"Osoba: {person.name} {person.surname}", normal_style))
                
                match_data = [["Podudarajuća imena na listi sankcija"]]
                for name in person.matching_names:
                    match_data.append([name])
                
                story.append(create_styled_table(match_data, [17*cm]))
                story.append(Spacer(1, 0.5*cm))
        # footer
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            "Ovaj dokument je automatski generiran i ne predstavlja pravno mišljenje. ",
            ParagraphStyle('Footer', parent=styles['Italic'], fontName=base_font, fontSize=8)
        ))
        
        # build PDF
        doc.build(story)