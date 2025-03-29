import os
from src.organizer import organize_files
from src.settings import load_settings
from src.logging import configure_logging, log_message  # Import log_message for logging


def main(settings=None):
    """Main function to manage the workflow."""
    try:
        configure_logging(log_mode="console", log_level="info", log_path=None)

        # If no settings are provided, attempt to load settings from the configuration file
        if settings is None:
            log_message(
                "info",
                "No settings provided. Attempting to load settings from the configuration file...",
            )
            settings = load_settings()

        settings.validate()
        configure_logging(settings.log_mode, settings.log_path, settings.log_level)

        # Ensure the fingerprint folder exists
        if not os.path.exists(settings.fingerprint_folder()):
            os.makedirs(settings.fingerprint_folder())

        # Start organizing files
        organize_files(settings)
    except Exception as e:
        log_message("error", f"Error: {e}")


if __name__ == "__main__":
    main()
