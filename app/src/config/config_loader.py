import json
import os

def get_config_json_path(file_name: str):
    """Get the path to the config.json file."""
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to config.json
    config_path = os.path.join(current_dir, file_name)
    return config_path

class Config:
    """
    A class to load and manage configuration settings from a JSON file.
    """
    def __init__(self, config_file_name: str):
        """Initialize the Config class and load the configuration from a JSON file."""

        config_file = get_config_json_path(config_file_name)

        with open(config_file, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    def get(self, key, default=None):
        return self.config.get(key, default)
    
app_config = Config('config.json')
assistant_config = Config('assistant.json')
