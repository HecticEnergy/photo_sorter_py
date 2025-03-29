import os
import sys
import argparse
from src.organizer import organize_files
from src.settings import ParserSettings, load_settings
from src.logging import configure_logging, log_message


def detect_execution_mode():
    """Detect whether the script is running interactively (CLI) or as a scheduled task."""
    return "console" if sys.stdin.isatty() else "scheduled"


def get_default_args():
    """Returns default arguments for the script."""
    mode = detect_execution_mode()
    return {
        "fingerprint_folder": os.path.join(".", ".settings", "fingerprints"),
        "date_format": "%Y-%m-%d_%H-%M-%S",
        "log_path": None,
        "log_mode": mode,
        "log_level": "info",
        "config": None,
        "config_folder": os.path.join(".", ".settings"),
    }


def parse_args():
    """Configures settings from command line arguments."""
    defaults = get_default_args()
    parser = argparse.ArgumentParser(description="File Organizer Settings")
    parser.add_argument("--input_folder", required=True, help="Input folder path")
    parser.add_argument("--output_folder", required=True, help="Output folder path")
    parser.add_argument(
        "--fingerprint_folder",
        default=defaults["fingerprint_folder"],
        help="Fingerprint folder path",
    )
    parser.add_argument(
        "--date_format", default=defaults["date_format"], help="Date format string"
    )
    parser.add_argument(
        "--log_path", default=defaults["log_path"], help="Log file path"
    )
    parser.add_argument(
        "--log_mode", default=defaults["log_mode"], help="Log mode (console/file)"
    )
    parser.add_argument("--log_level", default=defaults["log_level"], help="Log level")
    parser.add_argument(
        "--config", default=defaults["config"], help="Path to the configuration file"
    )
    parser.add_argument(
        "--config_folder",
        default=defaults["config_folder"],
        help="Path to the configuration folder",
    )
    return parser.parse_args()


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


def load_or_configure_settings():
    """Loads settings from a configuration file or command-line arguments."""
    log_message("info", "Attempting to load settings...")

    if detect_execution_mode() == "console":
        args = parse_args()
        # TODO: merge settings from config file and command line arguments (remove defaults first)
        if args.config:
            return load_settings(args.config)
        return configure_from_args(args)
    return load_settings()


def ensure_folders_exist(settings):
    """Ensures required folders exist."""
    fingerprint_folder = settings.fingerprint_folder()
    if not os.path.exists(fingerprint_folder):
        os.makedirs(fingerprint_folder)
        log_message("info", f"Created fingerprint folder: {fingerprint_folder}")


def run_workflow(settings):
    """Runs the main workflow."""
    try:
        organize_files(settings)
    except Exception as e:
        log_message("error", f"An error occurred during file organization: {e}")


def main():
    """Main function to manage the workflow."""
    try:
        # Configure initial logging
        configure_logging(log_mode="console", log_level="info", log_path=None)

        # Load or configure settings
        settings = load_or_configure_settings()

        # Validate settings
        settings.validate()

        # Configure logging based on settings
        configure_logging(settings.log_mode, settings.log_path, settings.log_level)

        # Ensure required folders exist
        ensure_folders_exist(settings)

        # Run the main workflow
        run_workflow(settings)

    except Exception as e:
        log_message("error", f"Critical error: {e}")


if __name__ == "__main__":
    main()
