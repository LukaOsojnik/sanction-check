import tkinter as tk
import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'
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
        
        self.root = tk.Tk()
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(AppConfig.WINDOW_SIZE)
        
        self.container = self._configure_dependencies()
        
        self.download_service = self.container.resolve(IDownloadService)
        self.processing_service = self.container.resolve(IProcessingService)
        self.ui_manager = self.container.resolve(IUIManager)
        
        self.controller = AppController(
            ui_manager=self.ui_manager,
            download_service=self.download_service,
            processing_service=self.processing_service
        )
        
        self.controller.initialize()
    
    def _configure_dependencies(self):
      
        container = DIContainer()
    
        container.register_instance(tk.Tk, self.root)
        
        container.register(IFileRepository, FileRepository)
        container.register(ISanctionsRepository, SanctionsRepository)
        
        container.register(IDownloadService, DownloadService)
        container.register(IProcessingService, ProcessingService)
        
        container.register(IUIManager, UIManager)
        
        return container
    
    def run(self):
    
        self.root.mainloop()

def main():
    app = SanctionsApp()
    app.run()

if __name__ == "__main__":
    main()
