class Person:
    def __init__(self, name, oib, address, count=0):
        self.name = name
        self.oib = oib
        self.address = address
        self.count = count
    
    def __str__(self):
        return f"Person(ime='{self.name}', oib='{self.oib}', address='{self.address}', count='{self.count}')"