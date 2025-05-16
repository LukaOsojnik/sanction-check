import os
import pandas as pd
from models.person import Person

def split_name_column(full_name):
    """
    The last word is treated as the name, everything else as the surname.
    """
    parts = str(full_name).strip().split()
    if len(parts) < 2:
        return "", parts[0] if parts else ""
    return " ".join(parts[:-1]), parts[-1]


class FileRepository:

    def load_people_from_file(self, file_path):
        """
        Load people from a csv or excel file.
        
        Parameters:
        file_path - Path to the file
        
        Returns:
        (people, message) - List of Person objects and status message
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.csv':
                df = pd.read_csv(file_path, delimiter=',')
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                return None, f"Unsupported file format: {file_ext}. Use CSV or Excel."

            required_columns = ['IME', 'OIB', 'ADRESA']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return None, f"Missing columns: {', '.join(missing_columns)}"

            people = []
            skipped_records = 0

            for _, row in df.iterrows():
                try:
                    raw_full_name = str(row['IME']).strip()
                    surname, name = split_name_column(raw_full_name)
                    oib = str(row['OIB']).strip()
                    address = str(row['ADRESA']).strip()

                    person = Person(name=name, surname=surname, oib=oib, address=address)
                    people.append(person)
                except Exception as e:
                    skipped_records += 1
                    print(f"Skipping invalid record {row.to_dict()}. Error: {e}")

            message = f"Loaded {len(people)} people."
            if skipped_records > 0:
                message += f" Skipped {skipped_records} invalid records."

            return people, message

        except Exception as e:
            return None, f"Error loading file: {str(e)}"