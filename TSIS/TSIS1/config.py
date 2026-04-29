import os
from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()

    
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, filename)

    parser.read(full_path)

    print("DEBUG PATH:", full_path)  

    config = {}
    if parser.has_section(section):
        for param in parser.items(section):
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {full_path} file')

    return config