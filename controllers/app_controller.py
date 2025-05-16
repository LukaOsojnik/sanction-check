import tkinter.messagebox as messagebox
import pandas as pd
from config import AppConfig

class AppController:
    def __init__(self, ui_manager, download_service, processing_service):
        """
        Initialize the controller with dependencies.
        
        Parameters:
        ui_manager - Manager for UI components
        download_service - Service for downloading data
        processing_service - Service for processing data
        """
        self.ui_manager = ui_manager
        self.download_service = download_service
        self.processing_service = processing_service
 
        self.sanctions_filename = None
        self.people_data = None
        self.people_file = None
        
    def initialize(self):
        """Initialize the application"""
        self.ui_manager.set_handlers(
            on_file_selected=self.handle_selected_file,
            on_start_processing=self.start_processing,
            on_return_to_welcome=self.show_welcome
        )

        self.ui_manager.show_welcome_screen()
        self.start_download_in_background()
    
    def handle_selected_file(self, file_path):
        """
        Handle file selection event.
        
        Parameters:
        file_path - Path to the selected file
        """
        self.ui_manager.update_welcome_status(f"Loading file: {file_path}...")
        
        # load file in background
        def on_file_loaded(people_data, message):
            """Callback when file is loaded"""
            self.people_data = people_data
            self.people_file = file_path if people_data else None
            
            if people_data:
                self.ui_manager.update_file_status(message, is_success=True)
            else:
                self.ui_manager.update_file_status(message, is_success=False)
        
        # start loading file
        self.processing_service.load_file_async(file_path, on_file_loaded)
    
    def start_download_in_background(self):
        """Download sanctions data in background"""
        self.ui_manager.update_welcome_status(AppConfig.MSG_DOWNLOADING)
        
        def on_download_complete(filename):
            """Callback when download is complete"""
            self.sanctions_filename = filename
            
            if filename:
                # get dataset date
                try:
                    df = pd.read_csv(filename, sep=";", low_memory=False) 
                    file_generation_date = df['fileGenerationDate'].iloc[0] if not df.empty else None 
                    
                    self.ui_manager.update_welcome_status(
                        f"Sanctions data loaded: {filename} as of {file_generation_date}."
                    )
                except Exception as e:
                    self.ui_manager.update_welcome_status(
                        f"Sanctions data loaded: {filename}"
                    )
            else:
                # update if error
                self.ui_manager.update_welcome_status(
                    AppConfig.MSG_DOWNLOAD_ERROR
                )

        # start download
        self.download_service.download_async(on_download_complete)
    
    def show_welcome(self):
        """Show welcome screen"""
        self.ui_manager.show_welcome_screen()
    
    def start_processing(self):
        """Start processing data"""
        if not self.people_data:
            messagebox.showwarning(
                "Missing Data", 
                AppConfig.MSG_NO_CLIENT_DATA
            )
            return
        
        self.ui_manager.show_sanctions_screen()
        
        if not self.sanctions_filename:
            # first is download of data
            self.ui_manager.update_sanctions_status(AppConfig.MSG_DOWNLOADING)
            
            self.download_service.download(
                on_complete=lambda filename: self._continue_processing(filename)
            )
        else:
            # already have sanctions data, continue processing
            self._continue_processing(self.sanctions_filename)
    
    def _continue_processing(self, sanctions_filename):
        """
        Continue processing with downloaded sanctions data.
        
        Parameters:
        sanctions_filename - Path to the sanctions data file
        """
        if not sanctions_filename:
            self.ui_manager.update_sanctions_status(AppConfig.MSG_DOWNLOAD_ERROR)
            return
            
        self.sanctions_filename = sanctions_filename
        self.ui_manager.update_sanctions_status(AppConfig.MSG_PROCESSING)
 
        # define callbacks for processing
        def on_progress(current, total):
            """Update progress bar"""
            self.ui_manager.update_sanctions_progress(current, total)
            
        def on_match_found(person):
            """Add person to results"""
            self.ui_manager.add_person_to_results(person)
            
        def on_complete(match_count, total_count):
            """Update status when processing is complete"""
            self.ui_manager.update_sanctions_status(
                AppConfig.MSG_COMPLETE.format(match_count)
            )

        # start processing
        self.processing_service.process_data(
            sanctions_filename=self.sanctions_filename,
            people_data=self.people_data,
            on_progress=on_progress,
            on_match_found=on_match_found,
            on_complete=on_complete
        )