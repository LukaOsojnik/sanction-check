from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Tuple, Any
from models.person import Person

# Service interfaces
class IDownloadService(ABC):
    @abstractmethod
    def download(self, on_complete: Optional[Callable] = None) -> str:
  
        pass
    
    @abstractmethod
    def download_async(self, on_complete: Optional[Callable] = None):
    
        pass
    

class IProcessingService(ABC):
    @abstractmethod
    def load_file_async(self, file_path: str, on_complete: Optional[Callable] = None):
     
        pass
    
    @abstractmethod
    def process_data(self, sanctions_filename: str, people_data: List[Person], 
                     on_progress: Optional[Callable] = None,
                     on_match_found: Optional[Callable] = None, 
                     on_complete: Optional[Callable] = None):
     
        pass

# UI interfaces
class IScreen(ABC):
    @abstractmethod
    def show(self):
       
        pass
    
    @abstractmethod
    def hide(self):
    
        pass

class IWelcomeScreen(IScreen):
    @abstractmethod
    def update_file_status(self, message: str, is_success: bool = True):
      
        pass
    
    @abstractmethod
    def update_status(self, message: str):
    
        pass

class ISanctionsScreen(IScreen):
    @abstractmethod
    def update_status(self, message: str):
   
        pass
    
    @abstractmethod
    def update_progress(self, current: int, total: int):
 
        pass
    
    @abstractmethod
    def add_person_object(self, person: Person):
    
        pass
    
    @abstractmethod
    def reset_progress(self):
     
        pass
    
    @abstractmethod
    def clear_table(self):
    
        pass

class IUIManager(ABC):
    @abstractmethod
    def set_handlers(self, on_file_selected: Callable, 
                    on_start_processing: Callable, 
                    on_return_to_welcome: Callable):
 
        pass
    
    @abstractmethod
    def show_welcome_screen(self):
     
        pass
    
    @abstractmethod
    def show_sanctions_screen(self):
     
        pass
    
    @abstractmethod
    def update_welcome_status(self, message: str):
    
        pass
    
    @abstractmethod
    def update_file_status(self, message: str, is_success: bool = True):

        pass
    
    @abstractmethod
    def update_sanctions_status(self, message: str):
    
        pass
    
    @abstractmethod
    def update_sanctions_progress(self, current: int, total: int):
     
        pass
    
    @abstractmethod
    def add_person_to_results(self, person: Person):
  
        pass

# Repository interfaces
class IFileRepository(ABC):
    @abstractmethod
    def load_people_from_file(self, file_path: str) -> Tuple[Optional[List[Person]], str]:
      
        pass

class ISanctionsRepository(ABC):
    @abstractmethod
    def download_sanctions_data(self) -> Optional[str]:
   
        pass
    
    @abstractmethod
    def process_sanctions_data(self, filename: str) -> Tuple[Any]:
     
        pass
    
    @abstractmethod
    def find_person_by_name(self, person_names_df: Any, search_name: str) -> Any:
       
        pass
