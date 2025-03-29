import logging
import sys


def configure_logging(log_mode, log_path, log_level="info"):
    """
    Configures logging based on log_mode, determining whether to log to console or file.

    Args:
        - log_mode: "console" or "file"
        - log_path: Path to the log file if logging to a file.
        - log_level: Logging level (default is INFO). Accepts logging levels like DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    if log_mode == "console":
        # Set up logging to the console
        logging.basicConfig(
            level=get_log_level(log_level),
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout)  # Logs to console
            ],
        )
    elif log_mode == "file":
        # Set up logging to a file
        logging.basicConfig(
            filename=log_path,
            level=get_log_level(log_level),
            format="%(asctime)s - %(levelname)s - %(message)s",
            filemode="a",  # Append to the log file
        )
    else:
        raise ValueError(
            f"Invalid log_mode specified: {log_mode}. Use 'console' or 'file'."
        )


def log_message(level, message):
    """
    Logs a message at the specified log level.

    Args:
        level (str): The level of the log (e.g., "info", "warning", "error").
        message (str): The message to log.
    """
    log_function = get_logger(level)
    if log_function:
        log_function(message)
    else:
        logging.error(f"Unknown log level: {level}. Logging as ERROR.")
        logging.error(message)


def get_log_level(level):
    """
    Maps string log levels to logging module constants.

    Args:
        level (str): The level of the log (e.g., "info", "warning", "error").

    Returns:
        int: Corresponding logging level constant.
    """

    log_levels = {
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "debug": logging.DEBUG,
        "critical": logging.CRITICAL,
    }
    return log_levels.get(level.lower(), logging.INFO)  # Default to INFO if not found

def get_logger(level):
    """
    Returns a logger configured with the specified log level.

    Args:
        level (str): The level of the log (e.g., "info", "warning", "error").

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_levels = {
        "info": logging.info,
        "warning": logging.warning,
        "error": logging.error,
        "debug": logging.debug,
        "critical": logging.critical,
    }
    return log_levels.get(level.lower(), logging.info)  # Default to INFO if not found