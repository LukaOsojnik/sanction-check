"""
Repository implementations for data access.
"""
import pandas as pd
import requests
import tempfile
import unicodedata

from typing import Optional, Tuple, Any
from interfaces import ISanctionsRepository
from utils import is_latin

class SanctionsRepository(ISanctionsRepository):
    """Repository for sanctions data operations"""
    
    def __init__(self):
        self.sanctions_url = "https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw"
    
    def download_sanctions_data(self) -> Optional[str]:
        """
        Download sanctions data from EU database
        
        Returns:
        str - Path to the downloaded file, or None if download failed
        """
        try:
            response = requests.get(self.sanctions_url)
            
            if response.status_code == 200:
                temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
                temp_file.write(response.content)
                temp_file_path = temp_file.name
                temp_file.close()
                print(f"Downloaded and saved to temp file: {temp_file_path}")
                return temp_file_path
            else:
                print(f"Error downloading CSV: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error during download: {e}")
            return None
    
    def process_sanctions_data(self, filename: str) -> Tuple[Any, Any]:
        """
        Process sanctions data file
        
        Parameters:
        filename - Path to the sanctions data file
        
        Returns:
        Tuple of (processed data DataFrame, file generation date)
        """
        try:
            # reading the file
            df = pd.read_csv(filename, sep=";", low_memory=False)

            # filtering by P
            persons_df = df[df['Entity_SubjectType'] == 'P']
            
            # grouping
            grouped = persons_df.groupby('Entity_LogicalId')

            person_names = grouped['NameAlias_WholeName'].apply(
                lambda name_series: [
                    name for name in name_series 
                    if pd.notna(name) and is_latin(name)
                        ]
                    ).reset_index()
            
            # filtering
            person_names = person_names[person_names['NameAlias_WholeName'].apply(len) > 0]
            
            return person_names
            
        except Exception as e:
            print(f"Error processing sanctions data: {e}")
            return None, None
    
    
    
    def find_person_by_name(self, person_names_df: Any, search_name: str) -> Any:

        def normalize(text: str) -> str:
            
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().replace('-', ' ').strip()
        
        search_tokens = set(normalize(search_name).split())

        def match_score(name_list):
            max_score = 0
            for name in name_list:
                name_tokens = set(normalize(name).split())
                direct_matches = len(search_tokens & name_tokens)

                partial_matches = 0
                for st in search_tokens:
                    for nt in name_tokens:
                        if st in nt and st != nt:
                            partial_matches += 1
                            break

                total_matches = direct_matches + partial_matches

                if total_matches < 2 and len(search_tokens) >= 2:
                    continue

                score = direct_matches + 0.5 * partial_matches
                max_score = max(max_score, score)

            return max_score

        person_names_df['match_score'] = person_names_df['NameAlias_WholeName'].apply(match_score)
        result = person_names_df[person_names_df['match_score'] > 0].sort_values(by='match_score', ascending=False)
        return result.drop(columns=['match_score'])
