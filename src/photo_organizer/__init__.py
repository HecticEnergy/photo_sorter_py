"""
Photo Organizer - A Python tool for organizing photos and videos by metadata.

This package provides functionality to:
- Extract metadata from photos and videos using ExifTool
- Organize files into date-based folder structures
- Handle duplicates and conflicts
- Provide comprehensive logging and dry-run capabilities
"""

__version__ = "1.0.0"
__author__ = "HecticEnergy"
__email__ = "contact@hecticenergy.com"

from .config_loader import ConfigLoader
from .metadata_parser import MetadataParser
from .fingerprint import FingerprintManager
from .file_mover import FileMover
from .logger import Logger
from .validator import ConfigValidator

__all__ = [
    "ConfigLoader",
    "MetadataParser", 
    "FingerprintManager",
    "FileMover",
    "Logger",
    "ConfigValidator"
]
