import os
import sys
import argparse
from src.organizer import organize_files
from src.settings import ParserSettings, load_settings
from src.logging import configure_logging, log_message  # Import log_message for logging


def configure_settings(settings=None):
    """Configures the logging settings."""
    if settings is None:
        settings = load_settings()
    configure_logging(settings.log_mode, settings.log_path, settings.log_level)
    return settings


def detect_execution_mode():
    """Detect whether the script is running interactively (CLI) or as a scheduled task."""
    if sys.stdin.isatty():
        return "console"
    else:
        return "scheduled"


def parse_args():
    mode = detect_execution_mode()
    """Configures settings from command line arguments."""
    parser = argparse.ArgumentParser(description="File Organizer Settings")
    parser.add_argument("--input_folder", required=True, help="Input folder path")
    parser.add_argument("--output_folder", required=True, help="Output folder path")
    parser.add_argument(
        "--fingerprint_folder", default="./.settings/", help="Fingerprint folder path"
    )
    parser.add_argument("--date_format", default="", help="Date format string")
    parser.add_argument("--log_path", default=None, help="Log file path")
    parser.add_argument("--log_mode", default=mode, help="Log mode (console/file)")
    parser.add_argument("--log_level", default="info", help="Log level")

    parser.add_argument("--config", default=None, help="Path to the configuration file")
    parser.add_argument(
        "--config_folder",
        default="./settings/",
        help="Path to the configuration folder",
    )

    args = parser.parse_args()
    return args


def configure_from_args(args):
    """Configures settings from command line arguments."""
    settings = ParserSettings(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        fingerprint_folder=args.fingerprint_folder,
        date_format=args.date_format,
        log_path=args.log_path,
        log_mode=args.log_mode,
        log_level=args.log_level,
    )
    settings.validate()  # Validate the settings
    return settings


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

            if detect_execution_mode() == "console":
                args = parse_args()
                if args.config is not None:
                    settings = load_settings(args.config)
                else:
                    settings = configure_from_args(args)
            else:
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
