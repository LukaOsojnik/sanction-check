class AppConfig:
   
    APP_NAME = "Sanctions Checker"
    VERSION = "1.0"
    
    # window settings
    WINDOW_TITLE = "Provjera sankcioniranih osoba"
    WINDOW_SIZE = "1024x640"
    
    # API
    SANCTIONS_API_URL = "https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw"
    
    # File columns
    REQUIRED_COLUMNS = ['IME','OIB', 'ADRESA']
    
    # UI messages
    MSG_DOWNLOADING = "Preuzimanje podataka o sankcijama..."
    MSG_DOWNLOAD_ERROR = "Greška pri preuzimanju podataka o sankcijama."
    MSG_PROCESSING = "Obrada podataka o sankcijama..."
    MSG_NO_CLIENT_DATA = "Morate najprije učitati datoteku s klijentima."
    MSG_COMPLETE = "Provjera završena. Pronađeno {} podudaranja."
    
    # File format messages
    MSG_UNSUPPORTED_FORMAT = "Nepodržani format datoteke: {}. Koristite CSV ili Excel."
    MSG_MISSING_COLUMNS = "Nedostaju stupci: {}"
    MSG_LOAD_SUCCESS = "Učitano {} osoba"
    MSG_SKIPPED_RECORDS = "Preskočeno {} nevažećih zapisa."
    MSG_LOAD_ERROR = "Greška pri učitavanju datoteke: {}"
