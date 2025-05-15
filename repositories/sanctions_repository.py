"""
Repository for sanctions data operations.
"""
import pandas as pd
import requests
from typing import Any
import tempfile
import unicodedata
from rapidfuzz import fuzz
from utils import is_latin
from config import AppConfig

class SanctionsRepository:
    """Repository for sanctions data operations"""
    
    def __init__(self):
        """Initialize the repository"""
        self.sanctions_url = AppConfig.SANCTIONS_API_URL
    
    def download_sanctions_data(self):
        """
        Download sanctions data from EU database.
        
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
    
    def process_sanctions_data(self, filename: str) -> pd.DataFrame:
        """
        Process sanctions data file
        
        Parameters:
        filename - Path to the sanctions data file
        
        Returns:
        DataFrame with processed name data
        """
        try:
            # read the file
            df = pd.read_csv(filename, sep=";", low_memory=False)

            # filtering by PEOPLE
            persons_df = df[df['Entity_SubjectType'] == 'P']

            name_columns = ['Entity_LogicalId', 'NameAlias_LastName', 'NameAlias_FirstName', 
                            'NameAlias_MiddleName', 'NameAlias_WholeName']
            
            existing_columns = [col for col in name_columns if col in persons_df.columns]
            
            # check for WholeName column
            if 'NameAlias_WholeName' not in existing_columns:
                print("Error: NameAlias_WholeName column not found in the data")
                return None
                
            selected_df = persons_df[existing_columns]
            
            # filter out rows where WholeName is not valid
            selected_df = selected_df[ 
                selected_df['NameAlias_WholeName'].apply(is_latin)
            ]
            # remove duplicates
            selected_df = selected_df.drop_duplicates()
            
            # check if there are any results
            if selected_df.empty:
                print("No valid names found in the data set")
                return None
                
            # print column names for debugging
            print(f"Columns in processed data: {selected_df.columns.tolist()}")

            return selected_df
            
        except Exception as e:
            print(f"Error processing sanctions data: {e}")
             
            return None
    
    def find_person_by_name(self, person_names_df: Any, person_name: str, person_surname: str) -> Any:
        
        def normalize(text: str) -> str:
            if not isinstance(text, str) or pd.isna(text):
                return ""
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().replace('-', ' ').strip()
        
        # normalize input
        normalized_name = normalize(person_name)
        normalized_surname = normalize(person_surname)
        
        # get name tokens (for prefix checking)
        name_tokens = normalized_name.split() if normalized_name else []
        
        # check which columns are available
        has_first_name = 'NameAlias_FirstName' in person_names_df.columns
        has_middle_name = 'NameAlias_MiddleName' in person_names_df.columns
        has_last_name = 'NameAlias_LastName' in person_names_df.columns
        
        # faster than rapid fuzz
        def check_prefix_match(short_name, long_name):
            """Check if short_name is a prefix of long_name"""
            if not short_name or not long_name:
                return False
                
            # A name can be a prefix if it's at least 3 characters
            if len(short_name) < 3:
                return False
                
            # is short name prefix of long name = (Ana - Analita / Dmitrij - Dmitrijevich)
            if long_name.startswith(short_name):
                # if name is prefix of the longer one - must have at least 3 letters and be 60% 
                if len(short_name) >= 3:
                    return True
                    
            return False
        
        def calculate_match_score(row):
            name_score = 0
            surname_score = 0
            
            # Simple matching - SURNAME 
            if normalized_surname and has_last_name and not pd.isna(row.get('NameAlias_LastName', pd.NA)):
                last_name = normalize(row['NameAlias_LastName'])
                if last_name:
                    # token_set_ratio with fuzz
                    surname_score = fuzz.token_set_ratio(normalized_surname, last_name) / 100.0
                    
                    # set score to 0 if bellow 0.80
                    if surname_score < 0.80:  # 80% threshold
                        surname_score = 0
            
            # Simple matching - NAME MATCHING 
            if name_tokens and has_first_name and not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                first_name = normalize(row['NameAlias_FirstName'])
                
                # is persons name prefix of alias
                if any(check_prefix_match(token, first_name) for token in name_tokens):
                    name_score = 0.85 # good match
                    # skip rapid fuzz for more efficiency
                    return surname_score * 0.6 + name_score * 0.4 if surname_score > 0 else 0
                
                # is alias's name prefix of persons
                elif any(check_prefix_match(first_name, token) for token in name_tokens):
                    name_score = 0.85
                    # skip rapid fuzz for more efficiency
                    return surname_score * 0.6 + name_score * 0.4 if surname_score > 0 else 0
            
            # if simple method not sufficient, use rapid fuzz library
            if normalized_name:
                # save first and middle name 
                alias_full_name = ""
                if has_first_name and not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                    alias_full_name += normalize(row['NameAlias_FirstName']) + " "
                if has_middle_name and not pd.isna(row.get('NameAlias_MiddleName', pd.NA)):
                    alias_full_name += normalize(row['NameAlias_MiddleName'])
                
                alias_full_name = alias_full_name.strip()
                
                if alias_full_name:
                    # token_set_ratio with fuzz
                    name_score = fuzz.token_set_ratio(normalized_name, alias_full_name) / 100.0
                    
                    # set score to 0 if bellow 0.80
                    if name_score < 0.70:  # 70% threshold
                        name_score = 0
            
            if surname_score > 0 and name_score > 0:
                return surname_score * 0.6 + name_score * 0.4
                
            return 0
        
        # apply scoring function
        person_names_df['match_score'] = person_names_df.apply(calculate_match_score, axis=1)
        
        # filter and sort
        result = person_names_df[person_names_df['match_score'] > 0].sort_values(
            by='match_score', ascending=False
        )
        
        return result.drop(columns=['match_score'])