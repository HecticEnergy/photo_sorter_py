"""
Configuration validator for Photo Organizer.

This module provides comprehensive validation of configuration values
to ensure they are valid before the organization process begins.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, NamedTuple

from .constants import (
    VALIDATION_PATTERNS, 
    SUPPORTED_IMAGE_EXTENSIONS, 
    SUPPORTED_VIDEO_EXTENSIONS,
    HashAlgorithm,
    LogMode,
    UnknownDateStrategy,
    ConflictResolution
)


class ValidationResult(NamedTuple):
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ConfigValidator:
    """Validates configuration values and provides detailed error reporting."""
    
    def __init__(self):
        """Initialize the validator."""
        self.errors = []
        self.warnings = []
    
    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate the complete configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        self.errors = []
        self.warnings = []
        
        # Validate required fields
        self._validate_required_fields(config)
        
        # Validate paths
        self._validate_paths(config)
        
        # Validate enum values
        self._validate_enum_values(config)
        
        # Validate format strings
        self._validate_format_strings(config)
        
        # Validate numeric values
        self._validate_numeric_values(config)
        
        # Validate file extensions
        self._validate_file_extensions(config)
        
        # Validate file permissions
        self._validate_permissions(config)
        
        # Validate logical consistency
        self._validate_logical_consistency(config)
        
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors.copy(),
            warnings=self.warnings.copy()
        )
    
    def _validate_required_fields(self, config: Dict[str, Any]) -> None:
        """Validate that required fields are present and not empty."""
        required_fields = {
            'input_folder': 'Input folder path',
            'output_folder': 'Output folder path',
        }
        
        for field, description in required_fields.items():
            if field not in config:
                self.errors.append(f"Missing required field: {field} ({description})")
            elif not config[field] or not str(config[field]).strip():
                self.errors.append(f"Required field cannot be empty: {field} ({description})")
    
    def _validate_paths(self, config: Dict[str, Any]) -> None:
        """Validate path-related configuration values."""
        # Input folder validation
        if 'input_folder' in config and config['input_folder']:
            input_path = Path(config['input_folder'])
            if not input_path.exists():
                self.errors.append(f"Input folder does not exist: {config['input_folder']}")
            elif not input_path.is_dir():
                self.errors.append(f"Input path is not a directory: {config['input_folder']}")
            elif not os.access(input_path, os.R_OK):
                self.errors.append(f"Input folder is not readable: {config['input_folder']}")
        
        # Output folder validation
        if 'output_folder' in config and config['output_folder']:
            output_path = Path(config['output_folder'])
            if output_path.exists():
                if not output_path.is_dir():
                    self.errors.append(f"Output path exists but is not a directory: {config['output_folder']}")
                elif not os.access(output_path, os.W_OK):
                    self.errors.append(f"Output folder is not writable: {config['output_folder']}")
            else:
                # Check if parent directory is writable
                try:
                    parent = output_path.parent
                    if not parent.exists():
                        self.warnings.append(f"Output folder parent directory will be created: {parent}")
                    elif not os.access(parent, os.W_OK):
                        self.errors.append(f"Cannot create output folder, parent not writable: {parent}")
                except Exception as e:
                    self.errors.append(f"Error checking output folder path: {e}")
        
        # Fingerprint folder validation
        if 'fingerprint_folder' in config and config['fingerprint_folder']:
            fp_path = Path(config['fingerprint_folder'])
            if fp_path.exists() and not fp_path.is_dir():
                self.errors.append(f"Fingerprint path exists but is not a directory: {config['fingerprint_folder']}")
        
        # Log file validation
        if 'log_path' in config and config['log_path']:
            log_path = Path(config['log_path'])
            if log_path.exists():
                if not log_path.is_file():
                    self.errors.append(f"Log path exists but is not a file: {config['log_path']}")
                elif not os.access(log_path, os.W_OK):
                    self.errors.append(f"Log file is not writable: {config['log_path']}")
            else:
                # Check if parent directory exists and is writable
                try:
                    parent = log_path.parent
                    if not parent.exists():
                        self.warnings.append(f"Log file parent directory will be created: {parent}")
                    elif not os.access(parent, os.W_OK):
                        self.errors.append(f"Cannot create log file, parent not writable: {parent}")
                except Exception as e:
                    self.errors.append(f"Error checking log file path: {e}")
    
    def _validate_enum_values(self, config: Dict[str, Any]) -> None:
        """Validate enum-based configuration values."""
        enum_validations = {
            'hash_algorithm': (HashAlgorithm, [e.value for e in HashAlgorithm]),
            'log_mode': (LogMode, [e.value for e in LogMode]),
            'unknown_strategy': (UnknownDateStrategy, [e.value for e in UnknownDateStrategy]),
            'filename_conflict_resolution': (ConflictResolution, [e.value for e in ConflictResolution]),
        }
        
        for field, (enum_class, valid_values) in enum_validations.items():
            if field in config and config[field] is not None:
                if config[field] not in valid_values:
                    self.errors.append(
                        f"Invalid {field}: '{config[field]}'. Valid values: {', '.join(valid_values)}"
                    )
    
    def _validate_format_strings(self, config: Dict[str, Any]) -> None:
        """Validate format string patterns."""
        if 'date_format' in config and config['date_format']:
            date_format = config['date_format']
            if not VALIDATION_PATTERNS['date_format'].search(date_format):
                self.errors.append(
                    f"Invalid date_format: '{date_format}'. Must contain at least one date/time placeholder (%Y, %m, %d, %H, %M, %S, %f)"
                )
            
            # Test the format string
            try:
                from datetime import datetime
                test_date = datetime.now()
                test_date.strftime(date_format)
            except ValueError as e:
                self.errors.append(f"Invalid date_format string: {e}")
    
    def _validate_numeric_values(self, config: Dict[str, Any]) -> None:
        """Validate numeric configuration values."""
        if 'verbose' in config:
            verbose = config['verbose']
            if not isinstance(verbose, int) or verbose < 0 or verbose > 3:
                self.errors.append(f"Invalid verbose level: {verbose}. Must be 0-3")
        
        if 'max_file_size_mb' in config:
            max_size = config['max_file_size_mb']
            if not isinstance(max_size, (int, float)) or max_size <= 0:
                self.errors.append(f"Invalid max_file_size_mb: {max_size}. Must be a positive number")
            elif max_size > 10240:  # 10GB
                self.warnings.append(f"Very large max_file_size_mb: {max_size}MB. This may cause memory issues")
    
    def _validate_file_extensions(self, config: Dict[str, Any]) -> None:
        """Validate that input folder contains supported file types."""
        if not config.get('input_folder'):
            return
        
        input_path = Path(config['input_folder'])
        if not input_path.exists() or not input_path.is_dir():
            return  # Path validation will handle this
        
        # Check if there are any supported files in the input directory
        supported_files = []
        unsupported_files = []
        
        try:
            # Scan for files (including nested if scan_nested is True)
            scan_nested = config.get('scan_nested', True)
            pattern = "**/*" if scan_nested else "*"
            
            for file_path in input_path.glob(pattern):
                if file_path.is_file():
                    extension = file_path.suffix.lower()
                    all_supported = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS
                    
                    if extension in all_supported:
                        supported_files.append(file_path)
                    else:
                        unsupported_files.append(file_path)
            
            # Provide feedback about file types found
            if not supported_files:
                if unsupported_files:
                    self.warnings.append(
                        f"No supported image/video files found in input folder. "
                        f"Found {len(unsupported_files)} unsupported files."
                    )
                else:
                    self.warnings.append("No files found in input folder.")
            else:
                image_count = sum(1 for f in supported_files 
                                if f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS)
                video_count = sum(1 for f in supported_files 
                                if f.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS)
                
                self.warnings.append(
                    f"Found {len(supported_files)} supported files "
                    f"({image_count} images, {video_count} videos)"
                )
                
                if unsupported_files and len(unsupported_files) > 10:
                    self.warnings.append(
                        f"Found {len(unsupported_files)} unsupported files that will be ignored"
                    )
        
        except Exception as e:
            self.warnings.append(f"Could not scan input folder for file types: {e}")
    
    def _validate_permissions(self, config: Dict[str, Any]) -> None:
        """Validate file system permissions for the operation."""
        if config.get('dry_run', False):
            # Skip permission checks in dry run mode
            return
        
        # Check if we can write to the output directory
        if 'output_folder' in config and config['output_folder']:
            output_path = Path(config['output_folder'])
            if output_path.exists():
                # Test write permission by creating a temporary file
                try:
                    test_file = output_path / '.write_test'
                    test_file.touch()
                    test_file.unlink()
                except Exception as e:
                    self.errors.append(f"Cannot write to output folder: {e}")
    
    def _validate_logical_consistency(self, config: Dict[str, Any]) -> None:
        """Validate logical consistency between configuration values."""
        # Check if input and output folders are the same
        if ('input_folder' in config and 'output_folder' in config and 
            config['input_folder'] and config['output_folder']):
            
            input_path = Path(config['input_folder']).resolve()
            output_path = Path(config['output_folder']).resolve()
            
            if input_path == output_path:
                self.errors.append("Input and output folders cannot be the same")
            
            # Check if output folder is inside input folder
            try:
                output_path.relative_to(input_path)
                self.warnings.append("Output folder is inside input folder. This may cause issues during organization")
            except ValueError:
                # output_path is not relative to input_path, which is good
                pass
        
        # Check log mode and log path consistency
        log_mode = config.get('log_mode', 'console')
        log_path = config.get('log_path')
        
        if log_mode in ['file', 'both'] and not log_path:
            self.errors.append("log_path must be specified when log_mode is 'file' or 'both'")
        
        # Check fingerprint folder consistency
        if not config.get('fingerprint_folder'):
            self.warnings.append("No fingerprint folder specified. Duplicate detection will not persist between runs")
    
    def validate_field(self, field_name: str, value: Any) -> ValidationResult:
        """
        Validate a single configuration field.
        
        Args:
            field_name: Name of the configuration field
            value: Value to validate
            
        Returns:
            ValidationResult for the single field
        """
        self.errors = []
        self.warnings = []
        
        config = {field_name: value}
        
        if field_name in ['input_folder', 'output_folder']:
            self._validate_paths(config)
        elif field_name in ['hash_algorithm', 'log_mode', 'unknown_strategy', 'filename_conflict_resolution']:
            self._validate_enum_values(config)
        elif field_name == 'date_format':
            self._validate_format_strings(config)
        elif field_name in ['verbose', 'max_file_size_mb']:
            self._validate_numeric_values(config)
        
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors.copy(),
            warnings=self.warnings.copy()
        )
