"""
Logging utilities for Photo Organizer.

This module provides both JSON-structured logging for automation
and human-readable console logging for interactive use.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .constants import LogLevel, LogMode


class Logger:
    """Multi-format logger supporting both console and file output."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the logger with configuration.
        
        Args:
            config: Configuration dictionary containing logging settings
        """
        self.config = config
        self.log_mode = config.get('log_mode', LogMode.CONSOLE.value)
        self.log_path = config.get('log_path')
        self.verbose = config.get('verbose', 0)
        self.dry_run = config.get('dry_run', False)
        
        # Initialize loggers
        self._setup_console_logger()
        self._setup_file_logger()
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        self.log_entries = []
    
    def _setup_console_logger(self) -> None:
        """Setup console logging configuration."""
        self.console_logger = logging.getLogger('photo_organizer_console')
        self.console_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.console_logger.handlers[:]:
            self.console_logger.removeHandler(handler)
        
        if self.log_mode in [LogMode.CONSOLE.value, LogMode.BOTH.value]:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            
            # Set level based on verbosity
            if self.verbose >= 3:
                console_handler.setLevel(logging.DEBUG)
            elif self.verbose >= 2:
                console_handler.setLevel(logging.INFO)
            elif self.verbose >= 1:
                console_handler.setLevel(logging.WARNING)
            else:
                console_handler.setLevel(logging.ERROR)
            
            # Format for console output
            console_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_format)
            self.console_logger.addHandler(console_handler)
    
    def _setup_file_logger(self) -> None:
        """Setup file logging configuration."""
        self.file_logger = logging.getLogger('photo_organizer_file')
        self.file_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.file_logger.handlers[:]:
            self.file_logger.removeHandler(handler)
        
        if self.log_mode in [LogMode.FILE.value, LogMode.BOTH.value] and self.log_path:
            # Ensure log directory exists
            log_file = Path(self.log_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # File handler
            file_handler = logging.FileHandler(self.log_path, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Format for file output (more detailed)
            file_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self.file_logger.addHandler(file_handler)
    
    def _log_to_structured(self, level: str, message: str, **kwargs) -> None:
        """Add entry to structured log for JSON output."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'level': level,
            'message': message,
            'dry_run': self.dry_run,
            **kwargs
        }
        self.log_entries.append(entry)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self.console_logger.debug(message)
        self.file_logger.debug(message)
        self._log_to_structured(LogLevel.DEBUG.value, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self.console_logger.info(message)
        self.file_logger.info(message)
        self._log_to_structured(LogLevel.INFO.value, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self.console_logger.warning(message)
        self.file_logger.warning(message)
        self._log_to_structured(LogLevel.WARNING.value, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log an error message."""
        self.console_logger.error(message)
        self.file_logger.error(message)
        self._log_to_structured(LogLevel.ERROR.value, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message."""
        self.console_logger.critical(message)
        self.file_logger.critical(message)
        self._log_to_structured(LogLevel.CRITICAL.value, message, **kwargs)
    
    def log_file_operation(self, operation: str, source: str, destination: str = None, 
                          status: str = "success", error: str = None) -> None:
        """
        Log a file operation with structured data.
        
        Args:
            operation: Type of operation (move, copy, skip, etc.)
            source: Source file path
            destination: Destination file path (if applicable)
            status: Operation status (success, error, skipped)
            error: Error message (if applicable)
        """
        message = f"{operation.title()}: {source}"
        if destination:
            message += f" -> {destination}"
        
        log_data = {
            'operation': operation,
            'source': source,
            'destination': destination,
            'status': status,
            'error': error
        }
        
        if status == "error":
            self.error(message, **log_data)
        elif status == "skipped":
            self.warning(message, **log_data)
        else:
            self.info(message, **log_data)
    
    def log_summary(self, summary: Dict[str, Any]) -> None:
        """
        Log session summary information.
        
        Args:
            summary: Dictionary containing summary statistics
        """
        session_duration = datetime.now() - self.session_start
        
        summary_message = (
            f"Session completed in {session_duration.total_seconds():.2f} seconds. "
            f"Moved: {summary.get('moved', 0)}, "
            f"Skipped: {summary.get('skipped', 0)}, "
            f"Duplicates: {summary.get('duplicates', 0)}, "
            f"Errors: {summary.get('errors', 0)}, "
            f"Unknown: {summary.get('unknown', 0)}"
        )
        
        self.info(summary_message, summary=summary, duration=session_duration.total_seconds())
    
    def get_structured_logs(self) -> list:
        """Get all structured log entries for the current session."""
        return self.log_entries.copy()
    
    def save_structured_logs(self, output_path: Optional[str] = None) -> None:
        """
        Save structured logs to a JSON file.
        
        Args:
            output_path: Optional path to save logs. If not provided, 
                        uses log_path with .json extension
        """
        if not output_path:
            if self.log_path:
                log_file = Path(self.log_path)
                output_path = str(log_file.with_suffix('.json'))
            else:
                output_path = f"photo_organizer_{self.session_id}.json"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        log_data = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'config': self.config,
                'total_entries': len(self.log_entries)
            },
            'entries': self.log_entries
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, default=str)
            self.info(f"Structured logs saved to: {output_path}")
        except Exception as e:
            self.error(f"Failed to save structured logs: {e}")
    
    def print_console_summary(self, summary: Dict[str, Any]) -> None:
        """
        Print a formatted summary to console.
        
        Args:
            summary: Dictionary containing summary statistics
        """
        if self.log_mode in [LogMode.CONSOLE.value, LogMode.BOTH.value]:
            print("\n" + "="*60)
            print("PHOTO ORGANIZER SUMMARY")
            print("="*60)
            print(f"Session ID: {self.session_id}")
            print(f"Dry Run: {'Yes' if self.dry_run else 'No'}")
            print(f"Duration: {(datetime.now() - self.session_start).total_seconds():.2f} seconds")
            print()
            print(f"Files moved:     {summary.get('moved', 0):,}")
            print(f"Files skipped:   {summary.get('skipped', 0):,}")
            print(f"Duplicates:      {summary.get('duplicates', 0):,}")
            print(f"Errors:          {summary.get('errors', 0):,}")
            print(f"Unknown dates:   {summary.get('unknown', 0):,}")
            print(f"Total processed: {sum(summary.values()):,}")
            print("="*60)
    
    def close(self) -> None:
        """Close all logging handlers and clean up resources."""
        # Close console logger handlers
        for handler in self.console_logger.handlers[:]:
            handler.close()
            self.console_logger.removeHandler(handler)
        
        # Close file logger handlers
        for handler in self.file_logger.handlers[:]:
            handler.close()
            self.file_logger.removeHandler(handler)
