import pandas as pd
import requests
from typing import Any
import tempfile
import unicodedata
from rapidfuzz import fuzz
from utils import is_latin
from config import AppConfig

class SanctionsRepository:
    """Repository for data operations"""
    
    def __init__(self):
        
        self.sanctions_url = AppConfig.SANCTIONS_API_URL
    
    def download_sanctions_data(self):
        """
        Download sanctions data with API.
        
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
        Save downloaded file

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

            return selected_df
            
        except Exception as e:
            print(f"Error processing sanctions data: {e}")
             
            return None
    
    def find_person_by_name(self, person_names_df: Any, person_name: str, person_surname: str) -> Any:
        """
        This functionsearches for matches in the sanctions data using the following approach:
        1. First tries to match individual name components (first name, surname)
        2. Falls back to whole name matching when individual components aren't available
        
        Parameters:
        person_names_df - DataFrame containing sanctions data with name components
        person_name - First name of the person to search for
        person_surname - Surname of the person to search for
        
        Returns:
        DataFrame containing matching records
        """

        SURNAME_THRESHOLD = 0.8   # 80% required for surnames
        NAME_THRESHOLD = 0.7      # 70% required for names
        TOKEN_SIMILARITY = 0.85   # 85% for token-level matching
        MIN_TOKEN_LENGTH = 3      # Minimum characters for a token to be considered
        
        def normalize(text: str) -> str:
            """Normalizes strings"""
            if not isinstance(text, str) or pd.isna(text):
                return ""
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().replace('-', ' ').strip()
        
        # normalize input
        normalized_name = normalize(person_name)
        normalized_surname = normalize(person_surname)
        
        # get name tokens for prefix checking
        name_tokens = normalized_name.split() if normalized_name else []
        
        # check which columns are available
        has_first_name = 'NameAlias_FirstName' in person_names_df.columns
        has_middle_name = 'NameAlias_MiddleName' in person_names_df.columns
        has_last_name = 'NameAlias_LastName' in person_names_df.columns
        
        def check_prefix_match(short_name, long_name):
            """Check if short_name is a prefix of long_name (e.g., Ana -> Analita)"""
            if not short_name or not long_name or len(short_name) < MIN_TOKEN_LENGTH:
                return False
            
            # ss short name prefix of long name (e.g., Ana -> Analita or Dmitrij -> Dmitrijevich)
            if long_name.startswith(short_name):
                return True
            
            return False
        
        def calculate_match_score(row):

            name_score = 0
            surname_score = 0
            
            # SURNAME MATCHING
            if normalized_surname and has_last_name and not pd.isna(row.get('NameAlias_LastName', pd.NA)):
                last_name = normalize(row['NameAlias_LastName'])
                if last_name:
                    surname_score = fuzz.token_set_ratio(normalized_surname, last_name) / 100.0
                    if surname_score < SURNAME_THRESHOLD:
                        surname_score = 0
            
            # NAME MATCHING
            if name_tokens and has_first_name and not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                first_name = normalize(row['NameAlias_FirstName'])
                
                # check for prefix matches (faster than fuzzy matching)
                if any(check_prefix_match(token, first_name) for token in name_tokens) or \
                any(check_prefix_match(first_name, token) for token in name_tokens):
                    name_score = 1
                
                # if no prefix match, try fuzzy matching
                elif normalized_name:
                    alias_full_name = ""
                    if not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                        alias_full_name += normalize(row['NameAlias_FirstName']) + " "
                    if has_middle_name and not pd.isna(row.get('NameAlias_MiddleName', pd.NA)):
                        alias_full_name += normalize(row['NameAlias_MiddleName'])
                    
                    alias_full_name = alias_full_name.strip()
                    
                    if alias_full_name:
                        name_score = fuzz.token_set_ratio(normalized_name, alias_full_name) / 100.0
                        if name_score < NAME_THRESHOLD:
                            name_score = 0

            if ((pd.isna(row.get('NameAlias_FirstName', pd.NA)) or pd.isna(row.get('NameAlias_LastName', pd.NA))) and 
                not pd.isna(row.get('NameAlias_WholeName', pd.NA))):
                whole_name = normalize(row['NameAlias_WholeName'])
                if whole_name:
                    # combine input name and surname
                    combined_name = f"{normalized_name} {normalized_surname}".strip()
                    if combined_name:
                        # split both names into tokens
                        combined_tokens = combined_name.split()
                        whole_tokens = whole_name.split()
                        
                        matching_token_count = 0
                        
                        # check each token in the input name
                        for input_token in combined_tokens:
                            # skip short tokens
                            if len(input_token) < MIN_TOKEN_LENGTH:
                                continue
                                
                            # check if token matches or is similar to any token in whole name
                            for whole_token in whole_tokens:
                                if len(whole_token) < MIN_TOKEN_LENGTH:
                                    continue
                                    
                                # check for exact match or high similarity
                                if input_token == whole_token or fuzz.ratio(input_token, whole_token) / 100.0 > TOKEN_SIMILARITY:
                                    matching_token_count += 1
                                    break 
                            
                            # Early termination once we have enough matches
                            if matching_token_count > 1:
                                name_score = 1
                                surname_score = 1
                                break 
            
            if surname_score > 0 and name_score > 0:
                return 1  
            return 0
        
        # apply scoring
        person_names_df['match_score'] = person_names_df.apply(calculate_match_score, axis=1)
        
        # filter matches
        result = person_names_df[person_names_df['match_score'] > 0]
        
        return result.drop(columns=['match_score'])