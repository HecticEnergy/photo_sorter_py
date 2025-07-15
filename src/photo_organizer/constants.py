"""
Constants and default values for the Photo Organizer.

This module contains regex patterns, enums, file type definitions,
and other constant values used throughout the application.
"""

import re
from enum import Enum
# Version information
VERSION = "1.0.0"

# Supported file extensions
SUPPORTED_IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp',
    '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw', '.dng', '.orf'
}

SUPPORTED_VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
    '.3gp', '.mts', '.m2ts', '.ts', '.vob', '.asf', '.rm', '.rmvb'
}

ALL_SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS

# Date format patterns for filename parsing
DATE_PATTERNS = [
    # ISO format: YYYY-MM-DD
    re.compile(r'(\d{4})[_-](\d{1,2})[_-](\d{1,2})'),
    # US format: MM-DD-YYYY or MM/DD/YYYY
    re.compile(r'(\d{1,2})[_/-](\d{1,2})[_/-](\d{4})'),
    # Timestamp format: YYYYMMDD_HHMMSS
    re.compile(r'(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})'),
    # IMG_YYYYMMDD format
    re.compile(r'IMG[_-](\d{4})(\d{2})(\d{2})'),
    # Screenshot format: Screenshot_YYYY-MM-DD
    re.compile(r'Screenshot[_-](\d{4})[_-](\d{1,2})[_-](\d{1,2})'),
]

# Time format patterns
TIME_PATTERNS = [
    # HH:MM:SS or HH-MM-SS
    re.compile(r'(\d{1,2})[:-](\d{1,2})[:-](\d{1,2})'),
    # HHMMSS
    re.compile(r'(\d{2})(\d{2})(\d{2})'),
]

# Configuration validation patterns
VALIDATION_PATTERNS = {
    'path': re.compile(r'^[a-zA-Z]:\\|^/|^\.'),  # Windows or Unix paths
    'date_format': re.compile(r'.*(%Y|%m|%d|%H|%M|%S|%f).*'),
    'log_file': re.compile(r'.*\.(log|txt)$'),
    'hash_algorithm': re.compile(r'^(sha256|md5|sha1)$'),
    'log_mode': re.compile(r'^(console|file|both)$'),
    'unknown_strategy': re.compile(r'^(route_to_unknown|use_ctime)$'),
    'conflict_resolution': re.compile(r'^(timestamp_suffix|uuid_suffix|overwrite)$'),
}

class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class UnknownDateStrategy(Enum):
    """Strategies for handling files with unknown dates."""
    ROUTE_TO_UNKNOWN = "route_to_unknown"
    USE_CTIME = "use_ctime"

class ConflictResolution(Enum):
    """Strategies for resolving filename conflicts."""
    TIMESTAMP_SUFFIX = "timestamp_suffix"
    UUID_SUFFIX = "uuid_suffix"
    OVERWRITE = "overwrite"

class HashAlgorithm(Enum):
    """Supported hash algorithms for duplicate detection."""
    SHA256 = "sha256"
    MD5 = "md5"
    SHA1 = "sha1"

class LogMode(Enum):
    """Logging output modes."""
    CONSOLE = "console"
    FILE = "file"
    BOTH = "both"

# Default configuration values
DEFAULT_CONFIG = {
    "input_folder": "",
    "output_folder": "",
    "fingerprint_folder": "fingerprints",
    "date_format": "%Y-%m-%d at %H-%M-%S (%f)",
    "log_path": "photo_organizer.log",
    "log_mode": LogMode.CONSOLE.value,
    "dry_run": False,
    "unknown_strategy": UnknownDateStrategy.ROUTE_TO_UNKNOWN.value,
    "scan_nested": True,
    "hash_algorithm": HashAlgorithm.SHA256.value,
    "filename_conflict_resolution": ConflictResolution.TIMESTAMP_SUFFIX.value,
    "verbose": 0,
    "max_file_size_mb": 1024,  # Maximum file size to process (in MB)
    "backup_originals": False,
    "preserve_folder_structure": False,
}

# EXIF metadata field mappings (in priority order)
EXIF_DATE_FIELDS = [
    # Primary creation date fields
    'DateTimeOriginal',           # EXIF date when photo was taken
    'EXIF:DateTimeOriginal',      # Prefixed version
    'CreateDate',                 # General creation date
    'EXIF:CreateDate',           # Prefixed version  
    'DateTime',                   # Generic date/time
    'EXIF:DateTime',             # Prefixed version
    
    # Video/QuickTime fields
    'QuickTime:CreateDate',
    'QuickTime:CreationDate',
    'CreationDate',
    
    # Sub-second precision versions
    'SubSecDateTimeOriginal',
    'SubSecCreateDate',
    
    # Alternative date fields
    'DateCreated',
    'ModifyDate',
    
    # File system fallbacks (lowest priority)
    'FileCreateDate',
    'File:FileCreateDate',
    'FileModifyDate',
    'File:FileModifyDate',
]

# Error messages
ERROR_MESSAGES = {
    'file_not_found': "File not found: {path}",
    'invalid_config': "Invalid configuration: {error}",
    'permission_denied': "Permission denied: {path}",
    'disk_full': "Insufficient disk space for operation",
    'corrupt_file': "File appears to be corrupted: {path}",
    'unsupported_format': "Unsupported file format: {path}",
    'duplicate_file': "Duplicate file detected: {path}",
}

# Success messages
SUCCESS_MESSAGES = {
    'file_moved': "Successfully moved: {source} -> {destination}",
    'fingerprint_saved': "Fingerprint database saved",
    'config_loaded': "Configuration loaded successfully",
    'process_complete': "Photo organization process completed",
}

# Buffer sizes for file operations
FILE_BUFFER_SIZE = 64 * 1024  # 64KB buffer for file operations
HASH_BUFFER_SIZE = 64 * 1024  # 64KB buffer for hash calculations

# Maximum number of retry attempts for file operations
MAX_RETRY_ATTEMPTS = 3

# Timeout values (in seconds)
EXIFTOOL_TIMEOUT = 30
FILE_OPERATION_TIMEOUT = 10
