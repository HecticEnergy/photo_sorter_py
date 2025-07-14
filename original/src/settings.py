import re
import json
import os


class ParserSettings:
    def __init__(
        self,
        input_folder,
        output_folder,
        fingerprint_folder,
        date_format,
        log_path,
        log_mode,
        log_level,
    ):
        self._input_folder = input_folder
        self._output_folder = output_folder
        self._fingerprint_folder = fingerprint_folder
        self._date_format = date_format
        self._log_path = log_path
        self._log_mode = log_mode
        self._log_level = log_level

    # Dynamic field functions
    def log_path(self):
        return self._log_path

    def log_mode(self):
        return self._log_mode

    def log_level(self):
        return self._log_level

    def input_folder(self):
        return self._input_folder

    def output_folder(self):
        return self._output_folder

    def fingerprint_folder(self):
        return self._fingerprint_folder

    def date_format(self):
        return self._date_format

    # validate log_level
    def validate_log_level(self):
        # Define a set of valid log levels
        valid_log_levels = {"info", "warning", "error", "debug", "critical"}
        if self._log_level not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {self._log_level}. Must be one of {valid_log_levels}."
            )

    def validate_log_mode(self):
        # Define a set of valid log modes
        valid_log_modes = {"console", "file"}
        if self._log_mode not in valid_log_modes:
            raise ValueError(
                f"Invalid log mode: {self._log_mode}. Must be one of {valid_log_modes}."
            )

    # Validation method for folders
    def validate_folders(self):
        # Define a pattern for allowed characters in folder paths
        folder_illegal_characters = r"[^a-zA-Z0-9_\-/\\:\s.]"

        # Check each folder field for illegal characters
        for field_name, field_value in {
            "input_folder": self._input_folder,
            "output_folder": self._output_folder,
            "fingerprint_folder": self._fingerprint_folder,
            "log_path": self._log_path,
        }.items():
            if re.search(folder_illegal_characters, field_value):
                raise ValueError(
                    f"Illegal characters detected in {field_name}: {field_value}"
                )

    # Validation method for date format
    def validate_date_format(self):
        # Define a list of valid strftime placeholders
        valid_placeholders = ["%Y", "%m", "%d", "%H", "%M", "%S", "%f"]
        # Extract all placeholders from the date format
        detected_placeholders = re.findall(r"%[A-Za-z]", self._date_format)

        for placeholder in detected_placeholders:
            if placeholder not in valid_placeholders:
                raise ValueError(
                    f"Invalid strftime placeholder detected in date_format: {placeholder}"
                )

        # Define illegal filename characters
        illegal_filename_characters = r'[<>:"/\\|?*]'

        # Substitute placeholders temporarily for checking filename validity
        example_filename = (
            self._date_format.replace("%Y", "2023")
            .replace("%m", "03")
            .replace("%d", "25")
            .replace("%H", "15")
            .replace("%M", "30")
            .replace("%S", "45")
            .replace("%f", "123")
        )

        if re.search(illegal_filename_characters, example_filename):
            raise ValueError(
                f"Illegal filename characters detected in date_format: {example_filename}"
            )

    # Validate both folders and date_format
    def validate(self):
        self.validate_folders()
        self.validate_date_format()
        self.validate_log_mode()
        self.validate_log_level()
        # Check log path validity
        if not os.path.isdir(os.path.dirname(self._log_path)):
            raise ValueError(f"Invalid log path directory: {self._log_path}")

    # Merge function
    @staticmethod
    def merge(settings1, settings2):
        """
        Merges two ParserSettings objects, replacing values in settings1
        with values from settings2, if they are populated.

        Args:
            settings1 (ParserSettings): The base settings object to be updated.
            settings2 (ParserSettings): The override settings object.

        Returns:
            ParserSettings: A new settings object with merged values.
        """
        merged_settings = ParserSettings(
            input_folder=settings2._input_folder or settings1._input_folder,
            output_folder=settings2._output_folder or settings1._output_folder,
            fingerprint_folder=settings2._fingerprint_folder
            or settings1._fingerprint_folder,
            date_format=settings2._date_format or settings1._date_format,
            log_path=settings2._log_path or settings1._log_path,
            log_mode=settings2._log_mode or settings1._log_mode,
            log_level=settings2._log_level or settings1._log_level,
        )
        return merged_settings


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
        required_keys = [
            "input_folder",
            "output_folder",
            "fingerprint_folder",
            "date_format",
            "log_path",
            "log_mode",
            "log_level",
        ]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")

        # Create and return the ParserSettings object
        settings = ParserSettings(
            input_folder=config["input_folder"],
            output_folder=config["output_folder"],
            fingerprint_folder=config["fingerprint_folder"],
            date_format=config["date_format"],
            log_path=config["log_path"],
            log_mode=config["log_mode"],
            log_level=config["log_level"],
        )
        settings.validate()  # Validate the settings
        return settings

    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing the settings file: {e}")
