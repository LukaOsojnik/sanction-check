import tkinter as tk

from di_container import DIContainer
from interfaces import (
    IDownloadService, IProcessingService, IUIManager,
    IFileRepository, ISanctionsRepository
)
# Correct imports for concrete implementations
from controllers.app_controller import AppController
from controllers.ui_manager import UIManager
from services.download_service import DownloadService  
from services.processing_service import ProcessingService 
from repositories.file_repository import FileRepository 
from repositories.sanctions_repository import SanctionsRepository 
from config import AppConfig

class SanctionsApp:
    def __init__(self):
        
        # Main window
        self.root = tk.Tk()
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(AppConfig.WINDOW_SIZE)
        
        # Set up dependency injection container
        self.container = self._configure_dependencies()
        
        # Resolve dependencies
        self.download_service = self.container.resolve(IDownloadService)
        self.processing_service = self.container.resolve(IProcessingService)
        self.ui_manager = self.container.resolve(IUIManager)
        
        # Application controller - with dependencies
        self.controller = AppController(
            ui_manager=self.ui_manager,
            download_service=self.download_service,
            processing_service=self.processing_service
        )
        
        self.controller.initialize()
    
    def _configure_dependencies(self):
      
        container = DIContainer()
        
        # Register the root window as an instance
        container.register_instance(tk.Tk, self.root)
        
        # Register repositories
        container.register(IFileRepository, FileRepository)
        container.register(ISanctionsRepository, SanctionsRepository)
        
        # Register services with dependencies
        container.register(IDownloadService, DownloadService)
        container.register(IProcessingService, ProcessingService)
        
        # Register UI manager
        container.register(IUIManager, UIManager)
        
        return container
    
    def run(self):
    
        self.root.mainloop()

def main():
    app = SanctionsApp()
    app.run()

if __name__ == "__main__":
    main()
