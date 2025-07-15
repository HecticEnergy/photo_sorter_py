"""
Metadata extraction and parsing for Photo Organizer.

This module handles extracting creation dates and other metadata from
photos and videos using ExifTool and fallback methods.
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from .constants import (
    EXIF_DATE_FIELDS,
    DATE_PATTERNS, 
    TIME_PATTERNS,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    EXIFTOOL_TIMEOUT,
    UnknownDateStrategy
)


class MetadataParser:
    """Handles metadata extraction from photos and videos."""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the metadata parser.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance for recording operations
        """
        self.config = config
        self.logger = logger
        self.unknown_strategy = config.get('unknown_strategy', UnknownDateStrategy.ROUTE_TO_UNKNOWN.value)
        
        # Locate ExifTool executable
        self.exiftool_path = self._find_exiftool()
        if not self.exiftool_path:
            self.logger.warning("ExifTool not found. Metadata extraction will be limited")
    
    def _find_exiftool(self) -> Optional[str]:
        """
        Find the ExifTool executable.
        
        Returns:
            Path to ExifTool executable or None if not found
        """
        # First, try the bundled ExifTool
        current_dir = Path(__file__).parent.parent.parent
        bundled_exiftool = current_dir / "exiftool.exe"
        
        if bundled_exiftool.exists():
            self.logger.debug(f"Found bundled ExifTool: {bundled_exiftool}")
            return str(bundled_exiftool)
        
        # Try alternative bundled location
        alt_bundled = current_dir / "exiftool_files" / "exiftool.exe"
        if alt_bundled.exists():
            self.logger.debug(f"Found bundled ExifTool: {alt_bundled}")
            return str(alt_bundled)
        
        # Try system PATH
        try:
            result = subprocess.run(['exiftool', '-ver'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.debug("Found ExifTool in system PATH")
                return 'exiftool'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file to extract metadata from
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_extension': file_path.suffix.lower(),
            'file_size': 0,
            'creation_date': None,
            'camera_make': None,
            'camera_model': None,
            'image_width': None,
            'image_height': None,
            'extraction_method': None,
            'error': None
        }
        
        try:
            # Get basic file info
            stat_info = file_path.stat()
            metadata['file_size'] = stat_info.st_size
            metadata['file_ctime'] = datetime.fromtimestamp(stat_info.st_ctime)
            metadata['file_mtime'] = datetime.fromtimestamp(stat_info.st_mtime)
            
            # Try ExifTool first
            creation_date = self._extract_with_exiftool(file_path, metadata)
            
            # Fallback to filename parsing if no date found
            if not creation_date:
                creation_date = self._extract_from_filename(file_path)
                if creation_date:
                    metadata['extraction_method'] = 'filename'
            
            # Final fallback based on strategy
            if not creation_date:
                if self.unknown_strategy == UnknownDateStrategy.USE_CTIME.value:
                    creation_date = metadata['file_ctime']
                    metadata['extraction_method'] = 'file_ctime'
                else:
                    metadata['extraction_method'] = 'unknown'
            
            metadata['creation_date'] = creation_date
            
        except Exception as e:
            metadata['error'] = str(e)
            self.logger.error(f"Error extracting metadata from {file_path}: {e}")
        
        return metadata
    
    def _extract_with_exiftool(self, file_path: Path, metadata: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract metadata using ExifTool.
        
        Args:
            file_path: Path to the file
            metadata: Metadata dictionary to update
            
        Returns:
            Creation date if found, None otherwise
        """
        if not self.exiftool_path:
            return None
        
        try:
            # Run ExifTool with JSON output
            cmd = [
                self.exiftool_path,
                '-json',
                '-charset', 'UTF8',
                '-api', 'largefilesupport=1',
                str(file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=EXIFTOOL_TIMEOUT,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                self.logger.debug(f"ExifTool failed for {file_path}: {result.stderr}")
                return None
            
            # Parse JSON output
            exif_data = json.loads(result.stdout)
            if not exif_data or not isinstance(exif_data, list):
                return None
            
            file_data = exif_data[0]
            
            # Extract additional metadata
            metadata['camera_make'] = file_data.get('Make')
            metadata['camera_model'] = file_data.get('Model')
            metadata['image_width'] = file_data.get('ImageWidth')
            metadata['image_height'] = file_data.get('ImageHeight')
            
            # Look for creation date in preferred order
            for field in EXIF_DATE_FIELDS:
                if field in file_data:
                    date_str = file_data[field]
                    if date_str:
                        creation_date = self._parse_exif_date(date_str)
                        if creation_date:
                            metadata['extraction_method'] = f'exif_{field}'
                            self.logger.debug(f"Found creation date via {field}: {creation_date}")
                            return creation_date
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"ExifTool timeout for {file_path}")
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse ExifTool JSON for {file_path}: {e}")
        except Exception as e:
            self.logger.debug(f"ExifTool error for {file_path}: {e}")
        
        return None
    
    def _parse_exif_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse an EXIF date string into a datetime object.
        
        Args:
            date_str: Date string from EXIF data
            
        Returns:
            Parsed datetime or None if parsing failed
        """
        if not date_str or date_str.strip() == "":
            return None
        
        # Common EXIF date formats
        date_formats = [
            "%Y:%m:%d %H:%M:%S",          # Standard EXIF format
            "%Y-%m-%d %H:%M:%S",          # ISO format
            "%Y:%m:%d %H:%M:%S.%f",       # With microseconds
            "%Y-%m-%d %H:%M:%S.%f",       # ISO with microseconds
            "%Y:%m:%d",                   # Date only
            "%Y-%m-%d",                   # ISO date only
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        self.logger.debug(f"Could not parse EXIF date: {date_str}")
        return None
    
    def _extract_from_filename(self, file_path: Path) -> Optional[datetime]:
        """
        Extract creation date from filename using regex patterns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted datetime or None if no date found
        """
        filename = file_path.stem
        
        for pattern in DATE_PATTERNS:
            match = pattern.search(filename)
            if match:
                try:
                    groups = match.groups()
                    
                    # Handle different pattern formats
                    if len(groups) >= 3:
                        # Basic date patterns
                        if len(groups[0]) == 4:  # YYYY format
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        else:  # MM/DD/YYYY format
                            month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                        
                        # Extract time if available
                        hour = minute = second = 0
                        if len(groups) >= 6:
                            hour, minute, second = int(groups[3]), int(groups[4]), int(groups[5])
                        
                        # Validate date components
                        if 1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 3000:
                            creation_date = datetime(year, month, day, hour, minute, second)
                            self.logger.debug(f"Extracted date from filename: {creation_date}")
                            return creation_date
                        
                except (ValueError, IndexError) as e:
                    self.logger.debug(f"Failed to parse date from filename {filename}: {e}")
                    continue
        
        return None
    
    def get_file_type(self, file_path: Path) -> str:
        """
        Determine the file type category.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File type category ('image', 'video', 'unknown')
        """
        extension = file_path.suffix.lower()
        
        if extension in SUPPORTED_IMAGE_EXTENSIONS:
            return 'image'
        elif extension in SUPPORTED_VIDEO_EXTENSIONS:
            return 'video'
        else:
            return 'unknown'
    
    def is_supported_file(self, file_path: Path) -> bool:
        """
        Check if the file type is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file type is supported, False otherwise
        """
        return self.get_file_type(file_path) != 'unknown'
    
    def validate_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate that a file can be processed.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not file_path.exists():
                return False, "File does not exist"
            
            # Check if it's a file (not directory)
            if not file_path.is_file():
                return False, "Path is not a file"
            
            # Check if file is supported
            if not self.is_supported_file(file_path):
                return False, f"Unsupported file type: {file_path.suffix}"
            
            # Check file size
            max_size_mb = self.config.get('max_file_size_mb', 1024)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > max_size_mb:
                return False, f"File too large: {file_size_mb:.1f}MB > {max_size_mb}MB"
            
            # Check read permissions
            if not os.access(file_path, os.R_OK):
                return False, "File is not readable"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {e}"
