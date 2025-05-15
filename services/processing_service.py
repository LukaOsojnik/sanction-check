"""
Service for processing sanctions data.
"""
import threading

class ProcessingService:
    def __init__(self, file_repository, sanctions_repository):
        """
        Initialize service with repositories.
        
        Parameters:
        file_repository - Repository for file operations
        sanctions_repository - Repository for sanctions data operations
        """
        self.file_repository = file_repository
        self.sanctions_repository = sanctions_repository
        
    def load_file_async(self, file_path, on_complete=None):
        """
        Load client data from file in background.
        
        Parameters:
        file_path - Path to the file
        on_complete - Function to call when done
        
        Returns:
        thread - The thread that is running the load operation
        """
        def load_thread():
            # Get people from file
            people_data, message = self.file_repository.load_people_from_file(file_path)
            
            if on_complete:
                on_complete(people_data, message)
        
        # Run in background thread
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def process_data(self, sanctions_filename, people_data, 
                    on_progress=None, 
                    on_match_found=None, 
                    on_complete=None):
        """
        Check client list against sanctions database.
        
        Parameters:
        sanctions_filename - CSV with sanctions data
        people_data - Clients to check
        on_progress - Updates UI progress bar
        on_match_found - Called when a match is found
        on_complete - Called when all checks are done
        
        Returns:
        thread - The thread that is running the process
        """
        def process_thread():
            # Get sanctions data 
            person_names = self.sanctions_repository.process_sanctions_data(sanctions_filename)
            if person_names is None:
                if on_complete:
                    on_complete(0, 0)
                return
                
            total_people = len(people_data)
            match_count = 0
            
            # Check each client against sanctions list
            for idx, person in enumerate(people_data):
                # Update progress bar
                if on_progress:
                    on_progress(idx, total_people)
                
                # Find matches for this person
                filtered_names = self.sanctions_repository.find_person_by_name(
                    person_names, person.name, person.surname
                )
                
                if not filtered_names.empty:
                    person.count += 1
                    
                    # Get IDs of all matching entities
                    matching_ids = filtered_names['Entity_LogicalId'].unique()
                    
                    # Find ALL aliases for these IDs
                    all_aliases = person_names[person_names['Entity_LogicalId'].isin(matching_ids)]
                    
                    # Store all alias names for matched entities
                    person.matching_names = []
                    for whole_name in all_aliases['NameAlias_WholeName'].tolist():
                        if isinstance(whole_name, list):
                            person.matching_names.extend(whole_name)
                        else:
                            person.matching_names.append(whole_name)
                    
                    # Add to results and update counter
                    if person.count > 0:
                        if on_match_found:
                            on_match_found(person)
                        match_count += 1
            
            # Show 100% complete when finished
            if on_progress:
                on_progress(total_people, total_people)
                
            # Report final results
            if on_complete:
                on_complete(match_count, total_people)

        # Run in background thread
        thread = threading.Thread(target=process_thread)
        thread.daemon = True
        thread.start()

        return thread