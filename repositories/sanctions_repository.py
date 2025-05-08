"""
Repository implementations for data access.
"""
import pandas as pd
import requests
import tempfile
import unicodedata

from typing import Optional, Any
from interfaces import ISanctionsRepository
from utils import is_latin
from rapidfuzz import fuzz

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
        
        def normalize(text: str) -> str:
            if not isinstance(text, str) or pd.isna(text):
                return ""
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('utf-8')
            return text.lower().replace('-', ' ').strip()
        
        # Normalize input
        normalized_name = normalize(person_name)
        normalized_surname = normalize(person_surname)
        
        # Get name tokens (for prefix checking)
        name_tokens = normalized_name.split() if normalized_name else []
        
        # Check which columns are available
        has_first_name = 'NameAlias_FirstName' in person_names_df.columns
        has_middle_name = 'NameAlias_MiddleName' in person_names_df.columns
        has_last_name = 'NameAlias_LastName' in person_names_df.columns
        
        def check_prefix_match(short_name, long_name):
            """Check if short_name is a prefix of long_name"""
            if not short_name or not long_name:
                return False
                
            # A name can be a prefix if it's at least 3 characters
            if len(short_name) < 3:
                return False
                
            # Check if short_name is at the beginning of long_name
            if long_name.startswith(short_name):
                # Determine if the prefix is significant (at least 60% of chars or 3+ chars)
                if len(short_name) >= 3 and len(short_name) >= 0.6 * len(long_name):
                    return True
                    
            return False
        
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
            
            # NAME MATCHING - Check for prefix match first (most efficient)
            if name_tokens and has_first_name and not pd.isna(row.get('NameAlias_FirstName', pd.NA)):
                first_name = normalize(row['NameAlias_FirstName'])
                
                # Check if the person's name is a prefix of the alias first name
                if any(check_prefix_match(token, first_name) for token in name_tokens):
                    name_score = 0.85  # Give a good score, but not perfect
                    # Skip the more expensive RapidFuzz check if we already have a match
                    return surname_score * 0.6 + name_score * 0.4 if surname_score > 0 else 0
                
                # Check if the alias first name is a prefix of the person's name
                elif any(check_prefix_match(first_name, token) for token in name_tokens):
                    name_score = 0.85
                    # Skip the more expensive RapidFuzz check if we already have a match
                    return surname_score * 0.6 + name_score * 0.4 if surname_score > 0 else 0
            
            # If we don't have a prefix match, proceed with RapidFuzz
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