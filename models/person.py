class Person:
    def __init__(self, name, oib, address, count=0, matching_names=None):
        self.name = name
        self.oib = oib
        self.address = address
        self.count = count
        self.matching_names = matching_names if matching_names is not None else []

    
    def __str__(self):
        return f"Person(ime='{self.name}', oib='{self.oib}', address='{self.address}', count='{self.count}')"