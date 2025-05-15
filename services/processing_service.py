import threading
from typing import List, Callable, Optional

from interfaces import IProcessingService, IFileRepository, ISanctionsRepository
from models.person import Person

class ProcessingService(IProcessingService):
    def __init__(self, 
                 file_repository: IFileRepository, 
                 sanctions_repository: ISanctionsRepository):
        """
        Setup service with repos we need
        """
        self.file_repository = file_repository
        self.sanctions_repository = sanctions_repository
        
    def load_file_async(self, file_path: str, on_complete: Optional[Callable] = None):
        """
        Load client data from file in background
        
        file_path - Where the file is
        on_complete - Function to call when done
        """
        def load_thread():
            # get people from file
            people_data, message = self.file_repository.load_people_from_file(file_path)
            
            if on_complete:
                on_complete(people_data, message)
        
        # run in background thread
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def process_data(self, sanctions_filename: str, people_data: List[Person], 
                    on_progress: Optional[Callable] = None, 
                    on_match_found: Optional[Callable] = None, 
                    on_complete: Optional[Callable] = None):
        """
        Check our client list against sanctions database
        
        sanctions_filename - CSV with sanctions data
        people_data - Our clients to check
        on_progress - Updates UI progress bar
        on_match_found - Called when we find a match
        on_complete - Called when all checks are done
        """
        def process_thread():
            # get sanctions data 
            person_names = self.sanctions_repository.process_sanctions_data(sanctions_filename)
            if person_names is None:
                if on_complete:
                    on_complete(0, 0)
                return
                
            total_people = len(people_data)
            match_count = 0
            
            # check each client against sanctions list
            for idx, person in enumerate(people_data):
                # update progress bar
                if on_progress:
                    on_progress(idx, total_people)
                
                # find matches for this person
                filtered_names = self.sanctions_repository.find_person_by_name(person_names, person.name, person.surname)
                
                if not filtered_names.empty:
                    person.count += 1
                    
                    # get IDs of all matching entities
                    matching_ids = filtered_names['Entity_LogicalId'].unique()
                    
                    # find ALL aliases for these IDs, not just the matching names
                    all_aliases = person_names[person_names['Entity_LogicalId'].isin(matching_ids)]
                    
                    # store all alias names for matched entities
                    person.matching_names = []
                    for whole_name in all_aliases['NameAlias_WholeName'].tolist():
                        if isinstance(whole_name, list):
                            person.matching_names.extend(whole_name)
                        else:
                            person.matching_names.append(whole_name)
                    
                    # add to results and update counter
                    if person.count > 0:
                        if on_match_found:
                            on_match_found(person)
                        match_count += 1
            
            # show 100% complete when finished
            if on_progress:
                on_progress(total_people, total_people)
                
            # report final results
            if on_complete:
                on_complete(match_count, total_people)

        # run in background thread
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

        return thread
        
        
    