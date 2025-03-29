import logging
from unittest.mock import patch, call
import pytest
from src.logging_wrapper import configure_logging


def test_configure_logging_console_mode():
    with (
        patch("logging.basicConfig") as mock_basic_config,
        patch("logging.StreamHandler") as mock_stream_handler,
    ):
        configure_logging(log_mode="console", log_path=None, log_level="debug")

        # Assert that logging.basicConfig was called with expected arguments for console mode
        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[mock_stream_handler.return_value],
        )


def test_configure_logging_file_mode():
    with patch("logging.basicConfig") as mock_basic_config:
        configure_logging(log_mode="file", log_path="test.log", log_level="error")

        # Assert that logging.basicConfig was called with expected arguments for file mode
        mock_basic_config.assert_called_once_with(
            filename="test.log",
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filemode="a",
        )


def test_configure_logging_invalid_mode():
    with pytest.raises(
        ValueError,
        match="Invalid log_mode specified: invalid. Use 'console' or 'file'.",
    ):
        configure_logging(log_mode="invalid", log_path=None, log_level="info")


def test_configure_logging_default_log_level():
    with (
        patch("logging.basicConfig") as mock_basic_config,
        patch("logging.StreamHandler") as mock_stream_handler,
    ):
        configure_logging(log_mode="console", log_path=None)

        # Assert that default log level is INFO
        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[mock_stream_handler.return_value],
        )


def test_log_message_info():
    with patch("logging.info") as mock_info:
        from src.logging import log_message

        log_message("info", "Test info message")
        mock_info.assert_called_once_with("Test info message")


def test_log_message_warning():
    with patch("logging.warning") as mock_warning:
        from src.logging import log_message

        log_message("warning", "Test warning message")
        mock_warning.assert_called_once_with("Test warning message")


def test_log_message_error():
    with patch("logging.error") as mock_error:
        from src.logging import log_message

        log_message("error", "Test error message")
        mock_error.assert_called_once_with("Test error message")


# def test_log_message_unknown_level():
#     with patch("logging.error") as mock_error:
#         from src.logging import log_message

#         log_message("unknown", "Test unknown level message")
#         mock_error.assert_called_once_with(
#             "Unknown log level: unknown. Logging as ERROR."
#         )
#         mock_error.assert_any_call("Test unknown level message")
