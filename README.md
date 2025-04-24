EU Sanctions Name Matcher

A tool for financial compliance teams to compare client names against the EU database of sanctioned individuals and entities.

Overview

This application helps compliance teams identify potential matches between client names and entities on EU sanctions lists, 
even when names have spelling variations, transliterations, or different formats. By using advanced name matching techniques, 
the tool reduces the risk of missing sanctioned entities due to name variations.

Key Features

Name normalization: Converts names to standardized formats to handle capitalization, accents, and special characters

Tokenization: Breaks names into meaningful components for more flexible partial matching

Transliteration awareness: Identifies matches across different spelling systems (e.g., 'Petrović', 'Petrovitch', 'Petrovitj')

Bulk processing: Upload and scan multiple client records simultaneously

Technical Implementation

The application employs several techniques to improve matching accuracy:

Unicode normalization

Character substitution rules for cross-alphabet matching

Token-based partial matching

CSV Format for Client Data

When using batch processing, your client CSV file should include the following columns:

Ime,OIB,ADRESA

Ivan Horvat,12312345670,"Osjecka ulica 2, Zagreb"

Ana Zaković,12345678901,"Vukovarska 123, Zagreb"


Note: The EU sanctions list is automatically imported and updated via API connection to the official EU database.

Data Sources

The application uses the official EU Consolidated Financial Sanctions List which is automatically updated when changes occur.

