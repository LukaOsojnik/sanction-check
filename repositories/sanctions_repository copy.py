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
    
    def process_sanctions_data(self, filename: str) -> pd.DataFrame:
        """
        Process sanctions data file
        
        Parameters:
        filename - Path to the sanctions data file
        
        Returns:
        DataFrame with processed name data
        """
        try:
            # Reading the file
            df = pd.read_csv(filename, sep=";", low_memory=False)

            # Filtering to get only persons
            persons_df = df[df['Entity_SubjectType'] == 'P']
            
            # Select only the columns we need
            name_columns = ['Entity_LogicalId', 'NameAlias_LastName', 'NameAlias_FirstName', 
                            'NameAlias_MiddleName', 'NameAlias_WholeName']
            
            # Ensure we only select columns that actually exist in the DataFrame
            existing_columns = [col for col in name_columns if col in persons_df.columns]
            
            # If WholeName is not in the existing columns, we can't proceed
            if 'NameAlias_WholeName' not in existing_columns:
                print("Error: NameAlias_WholeName column not found in the data")
                return None
                
            # Select the data with existing columns
            selected_df = persons_df[existing_columns]
            
            # Filter out rows where WholeName is not valid
            selected_df = selected_df[
                selected_df['NameAlias_WholeName'].notna() & 
                selected_df['NameAlias_WholeName'].apply(is_latin)
            ]
            
            # Group by Entity_LogicalId to handle multiple alias names for the same entity
            # Instead of applying a function to create lists, we'll keep all rows
            # This preserves the individual columns for FirstName, LastName, etc.
            
            # First, let's remove duplicates to avoid unnecessary processing
            selected_df = selected_df.drop_duplicates()
            
            # Check if there are any results
            if selected_df.empty:
                print("No valid names found in the sanctions data")
                return None
                
            # Print column names for debugging
            print(f"Columns in processed data: {selected_df.columns.tolist()}")
            
            # Return the processed DataFrame
            return selected_df
            
        except Exception as e:
            print(f"Error processing sanctions data: {e}")
             
            return None
    
    def find_person_by_name(self, person_names_df: Any, person_name: str, person_surname: str) -> Any:
        'Koristi RapidFuzz'
        def normalize(text: str) -> str:
            if not isinstance(text, str) or pd.isna(text):
                return ""
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().replace('-', ' ').strip()
        
        # Normalize input
        normalized_name = normalize(person_name)
        normalized_surname = normalize(person_surname)
        
        # Check which columns are available
        has_first_name = 'NameAlias_FirstName' in person_names_df.columns
        has_middle_name = 'NameAlias_MiddleName' in person_names_df.columns
        has_last_name = 'NameAlias_LastName' in person_names_df.columns
        
        def calculate_match_score(row):
            # Initialize scores
            name_score = 0
            surname_score = 0
            
            # SURNAME MATCHING
            if normalized_surname and has_last_name and not pd.isna(row.get('NameAlias_LastName', pd.NA)):
                last_name = normalize(row['NameAlias_LastName'])
                if last_name:
                    # Use token_set_ratio for handling word order differences
                    surname_score = fuzz.token_set_ratio(normalized_surname, last_name) / 100.0
                    
                    # Set to 0 if score is below threshold to avoid false positives
                    if surname_score < 0.80:  # 80% threshold
                        surname_score = 0
            
            # NAME MATCHING
            if normalized_name:
                # Collect first name and middle name for comparison
                alias_full_name = ""
                if has_first_name and not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                    alias_full_name += normalize(row['NameAlias_FirstName']) + " "
                if has_middle_name and not pd.isna(row.get('NameAlias_MiddleName', pd.NA)):
                    alias_full_name += normalize(row['NameAlias_MiddleName'])
                
                alias_full_name = alias_full_name.strip()
                
                if alias_full_name:
                    # Use token_set_ratio for name matching
                    name_score = fuzz.token_set_ratio(normalized_name, alias_full_name) / 100.0
                    
                    # Set to 0 if score is below threshold
                    if name_score < 0.75:  # 75% threshold
                        name_score = 0
            
            # Only consider it a match if both name and surname match
            if surname_score > 0 and name_score > 0:
                return surname_score * 0.6 + name_score * 0.4
                
            return 0
        
        # Apply the scoring function
        person_names_df['match_score'] = person_names_df.apply(calculate_match_score, axis=1)
        
        # Filter and sort results
        result = person_names_df[person_names_df['match_score'] > 0].sort_values(
            by='match_score', ascending=False
        )
        
        return result.drop(columns=['match_score'])
    
    def find_person_by_name(self, person_names_df: Any, person_name: str, person_surname: str) -> Any:
        'Bez RadidFuzzy-a'
        def normalize(text: str) -> str:
            if not isinstance(text, str) or pd.isna(text):
                return ""
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().replace('-', ' ').strip()
        
        # Normalize input
        normalized_name = normalize(person_name)
        normalized_surname = normalize(person_surname)
        
        # Get name tokens and surname tokens
        name_tokens = normalized_name.split() if normalized_name else []
        surname_tokens = normalized_surname.split() if normalized_surname else []
        
        # Check which columns are available
        has_first_name = 'NameAlias_FirstName' in person_names_df.columns
        has_middle_name = 'NameAlias_MiddleName' in person_names_df.columns
        has_last_name = 'NameAlias_LastName' in person_names_df.columns
        
        def match_tokens(search_tokens, comparison_tokens):
            """Match tokens using the original fast algorithm"""
            if not search_tokens or not comparison_tokens:
                return 0
                
            token_matched = [False] * len(search_tokens)
            match_scores = [0] * len(search_tokens)
            
            for i, st in enumerate(search_tokens):
                for nt in comparison_tokens:
                    # full match
                    if st == nt:
                        token_matched[i] = True
                        match_scores[i] = 1.0
                        break
                        
                    min_chars = min(len(st), len(nt))
                    if min_chars >= 3:  # samo ako je 3 ili više znakova
                        # provjera jeli search token substring name tokena
                        if st in nt and len(st) >= 0.8 * len(nt):
                            token_matched[i] = True
                            match_scores[i] = 0.9
                            break
                        # provjera name tokena u search tokenu
                        if nt in st and len(nt) >= 0.8 * len(st):
                            token_matched[i] = True
                            match_scores[i] = 0.9
                            break
                            
                        prefix_len = 0
                        for c in range(min(len(st), len(nt))):
                            if st[c] == nt[c]:
                                prefix_len += 1
                            else:
                                break
                        if prefix_len >= 3 and prefix_len >= 0.8 * min(len(st), len(nt)):
                            token_matched[i] = True
                            match_scores[i] = 0.8
                            break
            
            if all(token_matched):
                return sum(match_scores)
            return 0
        
        def calculate_match_score(row):
            """Calculate match score for a row using separate name/surname matching"""
            # Initialize scores
            name_score = 0
            surname_score = 0
            
            # SURNAME MATCHING
            if surname_tokens and has_last_name and not pd.isna(row.get('NameAlias_LastName', pd.NA)):
                last_name = normalize(row['NameAlias_LastName'])
                if last_name:
                    last_name_tokens = last_name.split()
                    surname_score = match_tokens(surname_tokens, last_name_tokens)
                    
            # NAME MATCHING
            if name_tokens:
                # Collect first name and middle name tokens for comparison
                name_comparison_tokens = []
                
                if has_first_name and not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                    first_name = normalize(row['NameAlias_FirstName'])
                    if first_name:
                        name_comparison_tokens.extend(first_name.split())
                        
                if has_middle_name and not pd.isna(row.get('NameAlias_MiddleName', pd.NA)):
                    middle_name = normalize(row['NameAlias_MiddleName'])
                    if middle_name:
                        name_comparison_tokens.extend(middle_name.split())
                        
                if name_comparison_tokens:
                    name_score = match_tokens(name_tokens, name_comparison_tokens)
            
            # If we have both name and surname matches, we have a valid match
            if surname_score > 0 and name_score > 0:
                # Weight surname slightly higher as it's usually more distinctive
                return surname_score * 0.6 + name_score * 0.4
                
            # If only one component matched, return a very reduced score (or 0 if you want to be strict)
            # Setting to 0 means we require both name AND surname to match
            return 0  # Change to return a small value if you want to allow partial matches
        
        # Apply the scoring function
        person_names_df['match_score'] = person_names_df.apply(calculate_match_score, axis=1)
        
        # Filter and sort results
        result = person_names_df[person_names_df['match_score'] > 0].sort_values(
            by='match_score', ascending=False
        )
        
        return result.drop(columns=['match_score'])
    
    