"""
Service for downloading and managing sanctions data.
"""
import threading
from interfaces import IDownloadService, ISanctionsRepository

class DownloadService(IDownloadService):
    def __init__(self, sanctions_repository: ISanctionsRepository):
        """
        Initialize with dependencies injected.
        
        Parameters:
        sanctions_repository - Repository for sanctions data operations
        """
        self.sanctions_repository = sanctions_repository
        self.cached_filename = None
    
    def download(self, on_complete=None):
        """
        Download sanctions data synchronously
        
        Parameters:
        on_complete - Callback function to call with the filename when complete
        """
        filename = self.sanctions_repository.download_sanctions_data()
        
        if filename:
            self.cached_filename = filename
            
        if on_complete:
            on_complete(filename)
            
        return filename
    
    def download_async(self, on_complete=None):
        """
        Download sanctions data asynchronously
        
        Parameters:
        on_complete - Callback function to call with the filename when complete
        """
        def download_thread():
            filename = self.download()
            
            if on_complete:
                on_complete(filename)
    
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        return thread
