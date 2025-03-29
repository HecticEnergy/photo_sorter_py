import re
import json
import os

class ParserSettings:
    def __init__(self, input_folder, output_folder, fingerprint_folder, date_format):
        self._input_folder = input_folder
        self._output_folder = output_folder
        self._fingerprint_folder = fingerprint_folder
        self._date_format = date_format

    # Dynamic field functions
    def input_folder(self):
        return self._input_folder

    def output_folder(self):
        return self._output_folder

    def fingerprint_folder(self):
        return self._fingerprint_folder

    def date_format(self):
        return self._date_format

    # Validation method for folders
    def validate_folders(self):
        # Define a pattern for allowed characters in folder paths
        folder_illegal_characters = r'[^a-zA-Z0-9_\-/\\:\s.]'

        # Check each folder field for illegal characters
        for field_name, field_value in {
            "input_folder": self._input_folder,
            "output_folder": self._output_folder,
            "fingerprint_folder": self._fingerprint_folder,
        }.items():
            if re.search(folder_illegal_characters, field_value):
                raise ValueError(f"Illegal characters detected in {field_name}: {field_value}")

    # Validation method for date format
    def validate_date_format(self):
        # Define a list of valid strftime placeholders
        valid_placeholders = ["%Y", "%m", "%d", "%H", "%M", "%S", "%f"]
        # Extract all placeholders from the date format
        detected_placeholders = re.findall(r"%[A-Za-z]", self._date_format)

        for placeholder in detected_placeholders:
            if placeholder not in valid_placeholders:
                raise ValueError(f"Invalid strftime placeholder detected in date_format: {placeholder}")

        # Define illegal filename characters
        illegal_filename_characters = r'[<>:"/\\|?*]'

        # Substitute placeholders temporarily for checking filename validity
        example_filename = self._date_format.replace("%Y", "2023") \
                                            .replace("%m", "03") \
                                            .replace("%d", "25") \
                                            .replace("%H", "15") \
                                            .replace("%M", "30") \
                                            .replace("%S", "45") \
                                            .replace("%f", "123")

        if re.search(illegal_filename_characters, example_filename):
            raise ValueError(f"Illegal filename characters detected in date_format: {example_filename}")

    # Validate both folders and date_format
    def validate(self):
        self.validate_folders()
        self.validate_date_format()


def load_settings(config_path="./settings/config.json"):
    """
    Loads settings from a configuration file and creates a ParserSettings object.

    Args:
        config_path (str): Path to the configuration JSON file.

    Returns:
        ParserSettings: Configured ParserSettings object.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Settings file not found at: {config_path}")

    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        
        # Validate required keys in the config file
        required_keys = ["input_folder", "output_folder", "fingerprint_folder", "date_format"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Create and return the ParserSettings object
        settings = ParserSettings(
            input_folder=config["input_folder"],
            output_folder=config["output_folder"],
            fingerprint_folder=config["fingerprint_folder"],
            date_format=config["date_format"]
        )
        settings.validate()  # Validate the settings
        return settings

    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing the settings file: {e}")
