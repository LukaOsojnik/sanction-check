import re

def is_latin(text):

    if not isinstance(text, str):
        return False
  
    latin_pattern = re.compile(r'^[A-Za-z0-9\s.,\'\-"()&;:!?čšćž]*$')

    return bool(latin_pattern.match(text))