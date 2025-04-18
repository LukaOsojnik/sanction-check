"""
Functions for downloading and caching sanctions data.
"""
import requests
import tempfile

def download_with_caching():

    csv_url = "https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw"
  
    try:
        response = requests.get(csv_url)
        
        if response.status_code == 200:
            temp_file = tempfile.NamedTemporaryFile(suffix = '.csv', delete = False)
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