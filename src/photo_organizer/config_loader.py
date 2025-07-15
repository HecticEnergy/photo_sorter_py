"""
Configuration loader for Photo Organizer.

This module handles loading, merging, and managing configuration from
JSON files and command line arguments.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .constants import DEFAULT_CONFIG, LogMode


class ConfigLoader:
    """Handles loading and merging configuration from multiple sources."""
    
    def __init__(self):
        """Initialize the ConfigLoader."""
        self.default_config = DEFAULT_CONFIG.copy()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get a copy of the default configuration."""
        return self.default_config.copy()
    
    def load_from_file(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            Dict containing the loaded configuration
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is invalid JSON
            ValueError: If the config file contains invalid values
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        if not config_file.is_file():
            raise ValueError(f"Configuration path is not a file: {config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file {config_path}: {e}")
        
        if not isinstance(file_config, dict):
            raise ValueError("Configuration file must contain a JSON object")
        
        # Start with defaults and update with file config
        config = self.default_config.copy()
        config.update(file_config)
        
        return config
    
    def merge_cli_args(self, config: Dict[str, Any], cli_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge command line arguments into the configuration.
        
        Args:
            config: Base configuration dictionary
            cli_args: CLI arguments to merge in
            
        Returns:
            Dict containing the merged configuration
        """
        merged_config = config.copy()
        
        # Map CLI argument names to config keys
        cli_mapping = {
            'input_folder': 'input_folder',
            'output_folder': 'output_folder',
            'dry_run': 'dry_run',
            'log_mode': 'log_mode',
            'verbose': 'verbose',
            'fingerprint_folder': 'fingerprint_folder',
            'log_path': 'log_path',
        }
        
        # Apply CLI arguments
        for cli_key, config_key in cli_mapping.items():
            if cli_key in cli_args and cli_args[cli_key] is not None:
                merged_config[config_key] = cli_args[cli_key]
        
        return merged_config
    
    def resolve_paths(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve relative paths to absolute paths in the configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict with resolved absolute paths
        """
        resolved_config = config.copy()
        
        # Path fields that should be resolved
        path_fields = [
            'input_folder',
            'output_folder', 
            'fingerprint_folder',
            'log_path'
        ]
        
        for field in path_fields:
            if field in resolved_config and resolved_config[field]:
                path = Path(resolved_config[field])
                if not path.is_absolute():
                    # Resolve relative to current working directory
                    resolved_config[field] = str(path.resolve())
                else:
                    resolved_config[field] = str(path)
        
        return resolved_config
    
    def create_directories(self, config: Dict[str, Any]) -> None:
        """
        Create necessary directories based on configuration.
        
        Args:
            config: Configuration dictionary
        """
        directories_to_create = []
        
        # Output folder
        if config.get('output_folder'):
            directories_to_create.append(config['output_folder'])
        
        # Fingerprint folder
        if config.get('fingerprint_folder'):
            directories_to_create.append(config['fingerprint_folder'])
        
        # Log file directory
        if config.get('log_path') and config.get('log_mode') in ['file', 'both']:
            log_dir = Path(config['log_path']).parent
            directories_to_create.append(str(log_dir))
        
        # Create directories
        for directory in directories_to_create:
            dir_path = Path(directory)
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise PermissionError(f"Cannot create directory: {directory}")
            except OSError as e:
                raise OSError(f"Error creating directory {directory}: {e}")
    
    def validate_required_fields(self, config: Dict[str, Any]) -> None:
        """
        Validate that required configuration fields are present and not empty.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValueError: If required fields are missing or empty
        """
        required_fields = ['input_folder', 'output_folder']
        
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
            elif not config[field] or not str(config[field]).strip():
                empty_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
        
        if empty_fields:
            raise ValueError(f"Required configuration fields cannot be empty: {', '.join(empty_fields)}")
    
    def save_config(self, config: Dict[str, Any], output_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config: Configuration dictionary to save
            output_path: Path where to save the configuration
        """
        output_file = Path(output_path)
        
        # Create directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert any enum values to strings for JSON serialization
        serializable_config = {}
        for key, value in config.items():
            if hasattr(value, 'value'):  # Enum type
                serializable_config[key] = value.value
            else:
                serializable_config[key] = value
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_config, f, indent=2, sort_keys=True)
        except OSError as e:
            raise OSError(f"Error saving configuration to {output_path}: {e}")
    
    def load_and_prepare_config(self, config_path: Optional[str] = None, 
                              cli_args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete configuration loading workflow.
        
        Args:
            config_path: Optional path to JSON config file
            cli_args: Optional CLI arguments to merge
            
        Returns:
            Dict containing the fully prepared configuration
        """
        # Load base configuration
        if config_path:
            config = self.load_from_file(config_path)
        else:
            config = self.get_default_config()
        
        # Merge CLI arguments
        if cli_args:
            config = self.merge_cli_args(config, cli_args)
        
        # Resolve paths
        config = self.resolve_paths(config)
        
        # Validate required fields
        self.validate_required_fields(config)
        
        # Create necessary directories
        if not config.get('dry_run', False):
            self.create_directories(config)
        
        return config
