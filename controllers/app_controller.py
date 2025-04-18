"""
Application controller for coordinating services and UI.
"""

import pandas as pd
import tkinter.messagebox as messagebox
from typing import Optional, List

from interfaces import IUIManager, IDownloadService, IProcessingService
from models.person import Person
from config import AppConfig

class AppController:
    def __init__(self, ui_manager: IUIManager, 
                 download_service: IDownloadService, 
                 processing_service: IProcessingService):
        """
        Initialize the application controller with injected dependencies.
        
        Parameters:
        ui_manager - Manager for UI components
        download_service - Service for downloading data
        processing_service - Service for processing data
        """
        self.ui_manager = ui_manager
        self.download_service = download_service
        self.processing_service = processing_service
 
        self.sanctions_filename: Optional[str] = None
        self.people_data: Optional[List[Person]] = None
        self.people_file: Optional[str] = None
        
    def initialize(self):

        self.ui_manager.set_handlers(
            on_file_selected=self.handle_selected_file,
            on_start_processing=self.start_processing,
            on_return_to_welcome=self.show_welcome
        )

        self.ui_manager.show_welcome_screen()

        self.start_download_in_background()
    
    def handle_selected_file(self, file_path: str):
        """Reports if file is loaded with is_success"""
        def on_file_loaded(people_data, message):

            self.people_data = people_data
            self.people_file = file_path if people_data else None
            
            if people_data:
                self.ui_manager.update_file_status(message, is_success=True)
            else:
                self.ui_manager.update_file_status(message, is_success=False)
        
        self.processing_service.load_file_async(file_path, on_file_loaded)
    
    def start_download_in_background(self):
        """Starts http request thread when the app starts"""
        self.ui_manager.update_welcome_status(AppConfig.MSG_DOWNLOADING)
        
        def on_download_complete(filename):

            self.sanctions_filename = filename
            
            if filename:
                df = pd.read_csv(filename, sep=";", low_memory=False) 
                file_generation_date = df['fileGenerationDate'].iloc[0] if not df.empty else None 
                self.ui_manager.update_welcome_status(f"Sankcionirana lista učitana i spremljena na lokaciju - {filename} as of {file_generation_date}.")
            else:
                self.ui_manager.update_welcome_status(AppConfig.MSG_DOWNLOAD_ERROR)

        self.download_service.download_async(on_download_complete)
    
    def show_welcome(self):
        
        self.ui_manager.show_welcome_screen()
    
    def start_processing(self):
        
        if not self.people_data:
            messagebox.showwarning(
                "Nedostaju podaci", 
                AppConfig.MSG_NO_CLIENT_DATA
            )
            return
        
        self.ui_manager.show_sanctions_screen()
        
        if not self.sanctions_filename:
           
            self.ui_manager.update_sanctions_status(AppConfig.MSG_DOWNLOADING)
            
            self.download_service.download(on_complete=lambda filename: self._continue_processing(filename))
            
        else:
       
            self._continue_processing(self.sanctions_filename)
    
    def _continue_processing(self, sanctions_filename):
    
        if not sanctions_filename:
            self.ui_manager.update_sanctions_status(AppConfig.MSG_DOWNLOAD_ERROR)
            return
            
        self.sanctions_filename = sanctions_filename
        self.ui_manager.update_sanctions_status(AppConfig.MSG_PROCESSING)
 
        # definded callbacks
        def on_progress(current, total):
            self.ui_manager.update_sanctions_progress(current, total)
            
        def on_match_found(person):
            self.ui_manager.add_person_to_results(person)
            
        def on_complete(match_count, total_count):
            self.ui_manager.update_sanctions_status(
                AppConfig.MSG_COMPLETE.format(match_count)
            )

        self.processing_service.process_data(
            sanctions_filename=self.sanctions_filename,
            people_data=self.people_data,
            on_progress=on_progress,
            on_match_found=on_match_found,
            on_complete=on_complete
        )
