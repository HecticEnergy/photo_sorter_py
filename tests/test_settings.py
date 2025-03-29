import pytest
from src.settings import ParserSettings


def test_settings_initialization():
    """Test that the ParserSettings object initializes correctly with valid inputs."""
    settings = ParserSettings(
        input_folder="C:/input",
        output_folder="C:/output",
        fingerprint_folder="C:/fingerprints",
        date_format="%Y-%m-%d_%H-%M-%S",
        log_path="C:/logs/app.log",
        log_mode="file",
        log_level="info",
    )

    assert settings.input_folder() == "C:/input"
    assert settings.output_folder() == "C:/output"
    assert settings.fingerprint_folder() == "C:/fingerprints"
    assert settings.date_format() == "%Y-%m-%d_%H-%M-%S"
    assert settings.log_path() == "C:/logs/app.log"
    assert settings.log_mode() == "file"
    assert settings.log_level() == "info"

def test_settings_log_level_validation():
    """Test that the log level validation raises an error for invalid log levels."""
    settings = ParserSettings(
        input_folder="C:/input",
        output_folder="C:/output",
        fingerprint_folder="C:/fingerprints",
        date_format="%Y-%m-%d_%H-%M-%S",
        log_path="C:/logs/app.log",
        log_mode="file",
        log_level="invalid_log_level",
    )

    with pytest.raises(ValueError, match="Invalid log level: invalid_log_level"):
        settings.validate_log_level()