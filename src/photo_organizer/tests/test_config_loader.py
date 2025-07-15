"""
Tests for the ConfigLoader module.
"""

import json
import pytest
import tempfile
from pathlib import Path

from photo_organizer.config_loader import ConfigLoader
from photo_organizer.constants import DEFAULT_CONFIG


class TestConfigLoader:
    """Test cases for ConfigLoader class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.loader = ConfigLoader()
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        config = self.loader.get_default_config()
        
        assert isinstance(config, dict)
        assert 'input_folder' in config
        assert 'output_folder' in config
        assert 'fingerprint_folder' in config
        
        # Should be a copy, not the original
        config['test_key'] = 'test_value'
        default_again = self.loader.get_default_config()
        assert 'test_key' not in default_again
    
    def test_load_from_file_valid_json(self):
        """Test loading valid JSON configuration file."""
        test_config = {
            "input_folder": "/test/input",
            "output_folder": "/test/output",
            "dry_run": True
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            config = self.loader.load_from_file(temp_path)
            
            # Should have default values merged with file values
            assert config['input_folder'] == "/test/input"
            assert config['output_folder'] == "/test/output"
            assert config['dry_run'] is True
            assert 'fingerprint_folder' in config  # Default value
            
        finally:
            Path(temp_path).unlink()
    
    def test_load_from_file_nonexistent(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_from_file("/path/that/does/not/exist.json")
    
    def test_load_from_file_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                self.loader.load_from_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_merge_cli_args(self):
        """Test merging CLI arguments with configuration."""
        base_config = self.loader.get_default_config()
        
        cli_args = {
            'input_folder': '/cli/input',
            'dry_run': True,
            'verbose': 2
        }
        
        merged = self.loader.merge_cli_args(base_config, cli_args)
        
        assert merged['input_folder'] == '/cli/input'
        assert merged['dry_run'] is True
        assert merged['verbose'] == 2
        
        # Original config should not be modified
        assert base_config['input_folder'] != '/cli/input'
    
    def test_validate_required_fields_valid(self):
        """Test validation with valid required fields."""
        config = {
            'input_folder': '/test/input',
            'output_folder': '/test/output'
        }
        
        # Should not raise any exception
        self.loader.validate_required_fields(config)
    
    def test_validate_required_fields_missing(self):
        """Test validation with missing required fields."""
        config = {
            'output_folder': '/test/output'
        }
        
        with pytest.raises(ValueError, match="Missing required configuration fields"):
            self.loader.validate_required_fields(config)
    
    def test_validate_required_fields_empty(self):
        """Test validation with empty required fields."""
        config = {
            'input_folder': '',
            'output_folder': '/test/output'
        }
        
        with pytest.raises(ValueError, match="Required configuration fields cannot be empty"):
            self.loader.validate_required_fields(config)
    
    def test_resolve_paths_relative(self):
        """Test resolving relative paths to absolute paths."""
        config = {
            'input_folder': './test/input',
            'output_folder': '../test/output',
            'log_path': 'test.log'
        }
        
        resolved = self.loader.resolve_paths(config)
        
        # All paths should now be absolute
        assert Path(resolved['input_folder']).is_absolute()
        assert Path(resolved['output_folder']).is_absolute()
        assert Path(resolved['log_path']).is_absolute()
    
    def test_resolve_paths_absolute(self):
        """Test that absolute paths remain unchanged."""
        config = {
            'input_folder': '/absolute/input',
            'output_folder': '/absolute/output'
        }
        
        resolved = self.loader.resolve_paths(config)
        
        assert resolved['input_folder'] == '/absolute/input'
        assert resolved['output_folder'] == '/absolute/output'
