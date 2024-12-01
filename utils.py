import json, os

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
    
def setting_default_environment() -> None:
    current_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_path)
    os.chdir(current_directory)