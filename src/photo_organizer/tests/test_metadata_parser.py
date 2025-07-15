"""
Tests for the MetadataParser module.
"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from photo_organizer.metadata_parser import MetadataParser
from photo_organizer.logger import Logger
from photo_organizer.constants import DEFAULT_CONFIG


class MockLogger:
    """Mock logger for testing."""
    
    def __init__(self):
        self.messages = []
    
    def debug(self, message, **kwargs):
        self.messages.append(('debug', message))
    
    def info(self, message, **kwargs):
        self.messages.append(('info', message))
    
    def warning(self, message, **kwargs):
        self.messages.append(('warning', message))
    
    def error(self, message, **kwargs):
        self.messages.append(('error', message))


class TestMetadataParser:
    """Test cases for MetadataParser class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = DEFAULT_CONFIG.copy()
        self.mock_logger = MockLogger()
        self.parser = MetadataParser(self.config, self.mock_logger)
    
    def test_parse_exif_date_standard_format(self):
        """Test parsing standard EXIF date format."""
        date_str = "2024:07:16 18:22:07"
        result = self.parser._parse_exif_date(date_str)
        
        assert result is not None
        assert result.year == 2024
        assert result.month == 7
        assert result.day == 16
        assert result.hour == 18
        assert result.minute == 22
        assert result.second == 7
    
    def test_parse_exif_date_iso_format(self):
        """Test parsing ISO date format."""
        date_str = "2024-07-16 18:22:07"
        result = self.parser._parse_exif_date(date_str)
        
        assert result is not None
        assert result.year == 2024
        assert result.month == 7
        assert result.day == 16
    
    def test_parse_exif_date_invalid(self):
        """Test parsing invalid date format."""
        date_str = "invalid date"
        result = self.parser._parse_exif_date(date_str)
        
        assert result is None
    
    def test_parse_exif_date_empty(self):
        """Test parsing empty date string."""
        result = self.parser._parse_exif_date("")
        assert result is None
        
        result = self.parser._parse_exif_date(None)
        assert result is None
    
    def test_extract_from_filename_iso_format(self):
        """Test extracting date from filename with ISO format."""
        test_file = Path("photo_2024-07-16_18-22-07.jpg")
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Rename to test filename
            new_path = temp_path.parent / "photo_2024-07-16_18-22-07.jpg"
            temp_path.rename(new_path)
            
            result = self.parser._extract_from_filename(new_path)
            
            assert result is not None
            assert result.year == 2024
            assert result.month == 7
            assert result.day == 16
            
        finally:
            if new_path.exists():
                new_path.unlink()
    
    def test_extract_from_filename_timestamp_format(self):
        """Test extracting date from filename with timestamp format."""
        test_file = Path("IMG_20240716_182207.jpg")
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Rename to test filename
            new_path = temp_path.parent / "IMG_20240716_182207.jpg"
            temp_path.rename(new_path)
            
            result = self.parser._extract_from_filename(new_path)
            
            assert result is not None
            assert result.year == 2024
            assert result.month == 7
            assert result.day == 16
            assert result.hour == 18
            assert result.minute == 22
            assert result.second == 7
            
        finally:
            if new_path.exists():
                new_path.unlink()
    
    def test_extract_from_filename_no_date(self):
        """Test extracting from filename with no recognizable date."""
        test_file = Path("random_photo_name.jpg")
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Rename to test filename
            new_path = temp_path.parent / "random_photo_name.jpg"
            temp_path.rename(new_path)
            
            result = self.parser._extract_from_filename(new_path)
            
            assert result is None
            
        finally:
            if new_path.exists():
                new_path.unlink()
    
    def test_get_file_type_image(self):
        """Test file type detection for images."""
        assert self.parser.get_file_type(Path("test.jpg")) == 'image'
        assert self.parser.get_file_type(Path("test.png")) == 'image'
        assert self.parser.get_file_type(Path("test.HEIC")) == 'image'
    
    def test_get_file_type_video(self):
        """Test file type detection for videos."""
        assert self.parser.get_file_type(Path("test.mp4")) == 'video'
        assert self.parser.get_file_type(Path("test.avi")) == 'video'
        assert self.parser.get_file_type(Path("test.MOV")) == 'video'
    
    def test_get_file_type_unknown(self):
        """Test file type detection for unknown files."""
        assert self.parser.get_file_type(Path("test.txt")) == 'unknown'
        assert self.parser.get_file_type(Path("test.doc")) == 'unknown'
    
    def test_is_supported_file(self):
        """Test supported file detection."""
        assert self.parser.is_supported_file(Path("test.jpg")) is True
        assert self.parser.is_supported_file(Path("test.mp4")) is True
        assert self.parser.is_supported_file(Path("test.txt")) is False
    
    def test_validate_file_nonexistent(self):
        """Test validation of non-existent file."""
        is_valid, error = self.parser.validate_file(Path("/path/that/does/not/exist.jpg"))
        
        assert is_valid is False
        assert "does not exist" in error
    
    def test_validate_file_unsupported_type(self):
        """Test validation of unsupported file type."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            is_valid, error = self.parser.validate_file(temp_path)
            
            assert is_valid is False
            assert "Unsupported file type" in error
            
        finally:
            temp_path.unlink()
    
    def test_extract_metadata_basic(self):
        """Test basic metadata extraction."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            metadata = self.parser.extract_metadata(temp_path)
            
            assert isinstance(metadata, dict)
            assert 'file_path' in metadata
            assert 'file_name' in metadata
            assert 'file_extension' in metadata
            assert 'file_size' in metadata
            assert metadata['file_extension'] == '.jpg'
            
        finally:
            temp_path.unlink()
