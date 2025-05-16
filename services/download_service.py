import threading

class DownloadService:
    def __init__(self, sanctions_repository):
        """
        Initialize with dependencies.
        
        Parameters:
        sanctions_repository - Repository for sanctions data operations
        """
        self.sanctions_repository = sanctions_repository
        self.cached_filename = None
    
    def download(self, on_complete=None):
        """
        Download sanctions data synchronously.
        
        Parameters:
        on_complete - Callback function to call with the filename when complete
        
        Returns:
        filename - Path to the downloaded file
        """
        filename = self.sanctions_repository.download_sanctions_data()
        
        if filename:
            self.cached_filename = filename
            
        if on_complete:
            on_complete(filename)
            
        return filename
    
    def download_async(self, on_complete=None):
        """
        Download sanctions data asynchronously.
        
        Parameters:
        on_complete - Callback function to call with the filename when complete
        
        Returns:
        thread - The thread that is running the download
        """
        def download_thread():
            filename = self.download()
            
            if on_complete:
                on_complete(filename)
    
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        return thread