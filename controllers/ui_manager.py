"""
UI Manager for handling screen transitions and updates.
"""
from typing import Callable
import tkinter as tk

from interfaces import IUIManager, IWelcomeScreen, ISanctionsScreen
from models.person import Person
from gui import WelcomeScreen, SanctionsScreen

class UIManager(IUIManager):
    def __init__(self, tk_root: tk.Tk):
        """
        Initialize the UI manager with injected root window
        
        Parameters:
        tk_root - The Tkinter root window
        """
        self.root = tk_root
        self.event_handlers = {
            'on_file_selected': None,
            'on_start_processing': None,
            'on_return_to_welcome': None
        }
        
        self.welcome_screen: IWelcomeScreen = None
        self.sanctions_screen: ISanctionsScreen = None
    
    def set_handlers(self, on_file_selected: Callable, 
                    on_start_processing: Callable, 
                    on_return_to_welcome: Callable):
     
        self.event_handlers['on_file_selected'] = on_file_selected
        self.event_handlers['on_start_processing'] = on_start_processing
        self.event_handlers['on_return_to_welcome'] = on_return_to_welcome
        
        self.welcome_screen = WelcomeScreen(
            self.root,
            on_start_callback=on_start_processing,
            on_file_drop_callback=on_file_selected
        )
        
        self.sanctions_screen = SanctionsScreen(
            self.root,
            on_back_callback=on_return_to_welcome
        )
    
    def show_welcome_screen(self):
   
        if self.sanctions_screen:
            self.sanctions_screen.hide()
        
        if self.welcome_screen:
            self.welcome_screen.show()
    
    def show_sanctions_screen(self):
   
        if self.welcome_screen:
            self.welcome_screen.hide()
            
        if self.sanctions_screen:
            self.sanctions_screen.show()
    
    def update_welcome_status(self, message: str):
      
        if self.welcome_screen:
            self.welcome_screen.update_status(message)
    
    def update_file_status(self, message: str, is_success: bool = True):
      
        if self.welcome_screen:
            self.welcome_screen.update_file_status(message, is_success)
    
    def update_sanctions_status(self, message: str):
    
        if self.sanctions_screen:
            self.sanctions_screen.update_status(message)
    
    def update_sanctions_progress(self, current: int, total: int):
       
        if self.sanctions_screen:
            self.sanctions_screen.update_progress(current, total)
    
    def add_person_to_results(self, person: Person):
    
        if self.sanctions_screen:
            self.sanctions_screen.add_person_object(person)
