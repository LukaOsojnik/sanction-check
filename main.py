import tkinter as tk

from config import AppConfig
from controllers.app_controller import AppController
from controllers.ui_manager import UIManager
from services.download_service import DownloadService
from services.processing_service import ProcessingService
from repositories.file_repository import FileRepository
from repositories.sanctions_repository import SanctionsRepository

class SanctionsApp:
    def __init__(self):
        # main window
        self.root = tk.Tk()
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(AppConfig.WINDOW_SIZE)
        
        # respoitories
        self.file_repository = FileRepository()
        self.sanctions_repository = SanctionsRepository()
        
        # services with dependencies
        self.download_service = DownloadService(self.sanctions_repository)
        self.processing_service = ProcessingService(
            self.file_repository, 
            self.sanctions_repository
        )
        
        # UI manager
        self.ui_manager = UIManager(self.root)
        
        # controller
        self.controller = AppController(
            self.ui_manager,
            self.download_service,
            self.processing_service
        )
        
        self.controller.initialize()
    
    def run(self):
        self.root.mainloop()

def main():
    app = SanctionsApp()
    app.run()

if __name__ == "__main__":
    main()