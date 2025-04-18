class DIContainer:
    """
    A simple dependency injection container.
    
    This class provides registration and resolution of dependencies,
    supporting constructor injection and singleton instances.
    """
    
    def __init__(self):
        self._registrations = {}
        self._instances = {}
    
    def register(self, interface_type, implementation_type, singleton=True):
        """
        Register an implementation for an interface.
        
        Parameters:
        interface_type - The interface/type to register
        implementation_type - The concrete implementation
        singleton - Whether to create a single instance (True) or new instance each time (False)
        """
        self._registrations[interface_type] = {
            'implementation': implementation_type,
            'singleton': singleton
        }
    
    def register_instance(self, interface_type, instance):
        """
        Register a pre-created instance.
        
        Parameters:
        interface_type - The interface/type to register
        instance - The instance to use
        """
        self._instances[interface_type] = instance
    
    def resolve(self, interface_type):
        """
        Resolve an implementation for the given interface.
        
        Parameters:
        interface_type - The interface to resolve
        
        Returns:
        An instance of the registered implementation
        """
   
        if interface_type in self._instances:
            return self._instances[interface_type]
        
        if interface_type not in self._registrations:
            raise ValueError(f"No registration found for {interface_type.__name__}")
        
        registration = self._registrations[interface_type]
        implementation_type = registration['implementation']
        
        import inspect
        params = {}
        signature = inspect.signature(implementation_type.__init__)
        
        for param_name, param in list(signature.parameters.items())[1:]:
            
            if param.annotation != inspect.Parameter.empty:
                params[param_name] = self.resolve(param.annotation)
        
    
        instance = implementation_type(**params)
        
        if registration['singleton']:
            self._instances[interface_type] = instance
        
        return instance
