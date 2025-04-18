"""
Repository implementations for data access.
"""
import os
import pandas as pd
from typing import List, Optional, Tuple, Any

from interfaces import IFileRepository
from models.person import Person

class FileRepository(IFileRepository):
    """Repository for file operations"""
    
    def load_people_from_file(self, file_path: str) -> Tuple[Optional[List[Person]], str]:
        """
        Load people data from CSV or Excel file.
        
        Parameters:
        file_path - Path to the CSV or Excel file
        
        Returns:
        Tuple of (list of Person objects or None, message)
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path, delimiter=',')
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                return None, f"Nepodržani format datoteke: {file_ext}. Koristite CSV ili Excel."
            
            # checks for column names
            required_columns = ['Ime', 'OIB', 'ADRESA']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return None, f"Nedostaju stupci: {', '.join(missing_columns)}"
            
            # persons object
            people = []
            skipped_records = 0
            
            for _, row in df.iterrows():
                try:
                    person = Person(row['Ime'], row['OIB'], row['ADRESA'])
                    people.append(person)
                except ValueError as e:
                    skipped_records += 1
                    print(f"Preskačem nevažeći zapis {row.to_dict()}. Greška: {e}")
            
            message = f"Učitano {len(people)} osoba"
            if skipped_records > 0:
                message += f" Preskočeno {skipped_records} nevažećih zapisa."
                
            return people, message
            
        except Exception as e:
            return None, f"Greška pri učitavanju datoteke: {str(e)}"
