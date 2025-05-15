"""
Repository implementations for data access.
"""
import os
import pandas as pd
from typing import List, Optional, Tuple

from interfaces import IFileRepository
from models.person import Person

def split_name_column(full_name: str) -> Tuple[str, str]:
    """
    Izvlači prezime i ime iz jedne kolone.
    Posljednja riječ se tretira kao ime, sve ostalo kao prezime.
    """
    parts = str(full_name).strip().split()
    if len(parts) < 2:
        return "", parts[0] if parts else ""
    return " ".join(parts[:-1]), parts[-1]


class FileRepository(IFileRepository):
    """Repository za rad s datotekama"""

    def load_people_from_file(self, file_path: str) -> Tuple[Optional[List[Person]], str]:
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.csv':
                df = pd.read_csv(file_path, delimiter=',')
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                return None, f"Nepodržani format datoteke: {file_ext}. Koristite CSV ili Excel."

            required_columns = ['IME', 'OIB', 'ADRESA']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return None, f"Nedostaju stupci: {', '.join(missing_columns)}"

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
                    print(f"Preskačem nevažeći zapis {row.to_dict()}. Greška: {e}")

            message = f"Učitano {len(people)} osoba."
            if skipped_records > 0:
                message += f" Preskočeno {skipped_records} nevažećih zapisa."

            return people, message

        except Exception as e:
            return None, f"Greška pri učitavanju datoteke: {str(e)}"

