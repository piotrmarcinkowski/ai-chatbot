import json
import os

def get_config_json_path():
    """Get the path to the config.json file."""
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to config.json
    config_path = os.path.join(current_dir, "config.json")
    return config_path

class ModelConfig:
    def __init__(self, config_file=get_config_json_path()):
        """Initialize the Config class and load the configuration from a JSON file."""

        with open(config_file, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    def get(self, key, default=None):
        return self.config.get(key, default)

model_config = ModelConfig()
