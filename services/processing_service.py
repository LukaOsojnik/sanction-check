import threading
from typing import List, Callable, Optional

from interfaces import IProcessingService, IFileRepository, ISanctionsRepository
from models.person import Person

class ProcessingService(IProcessingService):
    def __init__(self, 
                 file_repository: IFileRepository, 
                 sanctions_repository: ISanctionsRepository):
        """
        Initialize the processing service with injected dependencies
        
        Parameters:
        file_repository - Repository for file operations
        sanctions_repository - Repository for sanctions data
        """
        self.file_repository = file_repository
        self.sanctions_repository = sanctions_repository
        
    def load_file_async(self, file_path: str, on_complete: Optional[Callable] = None):
        """
        Load people data from a file asynchronously
        
        Parameters:
        file_path - Path to the file to load
        on_complete - Callback function to call with (people_data, message) when complete
        """
        def load_thread():
            # Load people data from file using the repository
            people_data, message = self.file_repository.load_people_from_file(file_path)
            
            if on_complete:
                on_complete(people_data, message)
        
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def process_data(self, sanctions_filename: str, people_data: List[Person], 
                    on_progress: Optional[Callable] = None, 
                    on_match_found: Optional[Callable] = None, 
                    on_complete: Optional[Callable] = None):
        """
        Process sanctions data against people data
        
        Parameters:
        sanctions_filename - Path to sanctions data file
        people_data - List of Person objects to check
        on_progress - Callback for progress updates (current, total)
        on_match_found - Callback when a match is found (person)
        on_complete - Callback when processing is complete (match_count, total_count)
        """
        def process_thread():
        
            person_names = self.sanctions_repository.process_sanctions_data(sanctions_filename)
            if person_names is None:
                if on_complete:
                    on_complete(0, 0)
                return
            
            total_people = len(people_data)
            match_count = 0
            
            for idx, person in enumerate(people_data):
        
                if on_progress:
                    on_progress(idx, total_people)
                
                filtered_names = self.sanctions_repository.find_person_by_name(person_names, person.name)
                
                if not filtered_names.empty:
                    person.count += 1
                    
                if person.count > 0:
                    if on_match_found:
                        on_match_found(person)
                    match_count += 1
            
            if on_progress:
                on_progress(total_people, total_people)
                
            if on_complete:
                on_complete(match_count, total_people)
        
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()
        
        return thread
