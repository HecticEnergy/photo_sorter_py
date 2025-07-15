"""
File movement and organization logic for Photo Organizer.

This module handles scanning directories, determining file destinations,
and performing file moves with conflict resolution.
"""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Generator, Optional

from .constants import (
    ALL_SUPPORTED_EXTENSIONS,
    ConflictResolution,
    UnknownDateStrategy,
    MAX_RETRY_ATTEMPTS
)


class FileMover:
    """Handles file scanning, destination logic, and file operations."""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the file mover.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance for recording operations
        """
        self.config = config
        self.logger = logger
        self.input_folder = Path(config['input_folder'])
        self.output_folder = Path(config['output_folder'])
        self.dry_run = config.get('dry_run', False)
        self.scan_nested = config.get('scan_nested', True)
        self.conflict_resolution = config.get('filename_conflict_resolution', ConflictResolution.TIMESTAMP_SUFFIX.value)
        self.unknown_strategy = config.get('unknown_strategy', UnknownDateStrategy.ROUTE_TO_UNKNOWN.value)
        self.date_format = config.get('date_format', '%Y-%m-%d at %H-%M-%S (%f)')
        
        # Track copied files to prevent duplicate processing
        self.copied_files = set()
    
    def scan_files(self, input_path: Path) -> Generator[Path, None, None]:
        """
        Scan directory for supported files.
        
        Args:
            input_path: Path to scan for files
            
        Yields:
            Path objects for each supported file found
        """
        try:
            if self.scan_nested:
                # Recursive scan
                pattern = "**/*"
            else:
                # Single level scan
                pattern = "*"
            
            for file_path in input_path.glob(pattern):
                if file_path.is_file() and self._is_supported_file(file_path):
                    yield file_path
                    
        except Exception as e:
            self.logger.error(f"Error scanning directory {input_path}: {e}")
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """
        Check if a file is supported based on its extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file is supported, False otherwise
        """
        extension = file_path.suffix.lower()
        return extension in ALL_SUPPORTED_EXTENSIONS
    
    def determine_destination(self, file_path: Path, metadata: Dict[str, Any]) -> Path:
        """
        Determine the destination path for a file based on its metadata.
        
        Args:
            file_path: Source file path
            metadata: File metadata dictionary
            
        Returns:
            Destination path for the file
        """
        creation_date = metadata.get('creation_date')
        
        if creation_date and isinstance(creation_date, datetime):
            # Standard date-based organization
            year_folder = creation_date.strftime("%Y")
            month_folder = creation_date.strftime("%m")
            destination_dir = self.output_folder / year_folder / month_folder
        else:
            # Handle unknown dates based on strategy
            if self.unknown_strategy == UnknownDateStrategy.USE_CTIME.value:
                # Use file creation time
                ctime = metadata.get('file_ctime')
                if ctime:
                    year_folder = ctime.strftime("%Y")
                    month_folder = ctime.strftime("%m")
                    destination_dir = self.output_folder / year_folder / month_folder
                else:
                    destination_dir = self.output_folder / "unknown"
            else:
                # Route to unknown folder with preserved structure
                destination_dir = self.output_folder / "unknown"
                
                # Preserve relative path structure for unknown files
                relative_path = file_path.relative_to(self.input_folder)
                if len(relative_path.parts) > 1:
                    # File is in a subdirectory, preserve the structure
                    destination_dir = destination_dir / relative_path.parent
        
        # Generate filename
        filename = self._generate_filename(file_path, metadata, creation_date)
        destination_path = destination_dir / filename
        
        # Resolve conflicts
        destination_path = self._resolve_filename_conflict(destination_path)
        
        return destination_path
    
    def _generate_filename(self, file_path: Path, metadata: Dict[str, Any], creation_date: Optional[datetime]) -> str:
        """
        Generate the destination filename based on the date format and metadata.
        
        Args:
            file_path: Source file path
            metadata: File metadata
            creation_date: Creation date if available
            
        Returns:
            Generated filename
        """
        original_extension = file_path.suffix
        
        if creation_date:
            try:
                # Use the configured date format
                base_name = creation_date.strftime(self.date_format)
                
                # Handle microseconds formatting - if all zeros, use a sequence number instead
                if '%f' in self.date_format and creation_date.microsecond == 0:
                    # Replace microseconds with a 3-digit counter based on file name or use random
                    import hashlib
                    file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:3]
                    base_name = base_name.replace('000000', file_hash.upper())
                elif '%f' in self.date_format:
                    # Convert microseconds to milliseconds (3 digits) for shorter names
                    milliseconds = f"{creation_date.microsecond // 1000:03d}"
                    base_name = base_name.replace(f"{creation_date.microsecond:06d}", milliseconds)
                
            except ValueError as e:
                self.logger.warning(f"Error formatting date with format '{self.date_format}': {e}")
                base_name = file_path.stem
        else:
            # Use original filename for unknown dates
            base_name = file_path.stem
        
        # Ensure filename is filesystem-safe
        base_name = self._sanitize_filename(base_name)
        
        return f"{base_name}{original_extension}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Replace filesystem-unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        filename = filename.strip('. ')
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed_file"
        
        # Limit filename length (Windows has 255 char limit for full path)
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def _resolve_filename_conflict(self, destination_path: Path) -> Path:
        """
        Resolve filename conflicts using the configured strategy.
        
        Args:
            destination_path: Proposed destination path
            
        Returns:
            Resolved destination path without conflicts
        """
        if not destination_path.exists():
            return destination_path
        
        base_path = destination_path.parent
        stem = destination_path.stem
        suffix = destination_path.suffix
        
        if self.conflict_resolution == ConflictResolution.TIMESTAMP_SUFFIX.value:
            # Add timestamp suffix
            timestamp = datetime.now().strftime("%H%M%S")
            counter = 1
            
            while True:
                new_stem = f"{stem}_{timestamp}_{counter:03d}"
                new_path = base_path / f"{new_stem}{suffix}"
                
                if not new_path.exists():
                    return new_path
                
                counter += 1
                if counter > 999:
                    # Fall back to UUID if too many conflicts
                    new_stem = f"{stem}_{uuid.uuid4().hex[:8]}"
                    return base_path / f"{new_stem}{suffix}"
        
        elif self.conflict_resolution == ConflictResolution.UUID_SUFFIX.value:
            # Add UUID suffix
            new_stem = f"{stem}_{uuid.uuid4().hex[:8]}"
            return base_path / f"{new_stem}{suffix}"
        
        elif self.conflict_resolution == ConflictResolution.OVERWRITE.value:
            # Allow overwrite (return original path)
            self.logger.warning(f"File will be overwritten: {destination_path}")
            return destination_path
        
        else:
            # Default to timestamp suffix
            timestamp = datetime.now().strftime("%H%M%S")
            new_stem = f"{stem}_{timestamp}"
            return base_path / f"{new_stem}{suffix}"
    
    def copy_file(self, source_path: Path, destination_path: Path) -> bool:
        """
        Copy a file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if file was copied successfully, False otherwise
        """
        try:
            # Check if file has already been processed in this session
            if str(source_path) in self.copied_files:
                self.logger.debug(f"File already processed in this session: {source_path}")
                return False
            
            # Ensure destination directory exists
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.dry_run:
                # Simulate the copy
                self.logger.info("[DRY RUN] Would copy file:")
                self.logger.info(f"  Source: {source_path}")
                self.logger.info(f"  Dest:   {destination_path}")
                self.logger.info(f"  Size:   {source_path.stat().st_size if source_path.exists() else 'unknown'} bytes")
                self.copied_files.add(str(source_path))
                return True
            
            # Perform the actual copy with retry logic
            for attempt in range(MAX_RETRY_ATTEMPTS):
                try:
                    # Check if source file still exists
                    if not source_path.exists():
                        self.logger.warning(f"Source file no longer exists: {source_path}")
                        return False
                    
                    # Perform the copy
                    shutil.copy2(str(source_path), str(destination_path))
                    
                    # Verify the copy was successful
                    if destination_path.exists():
                        file_size = destination_path.stat().st_size
                        self.logger.debug("Successfully copied file:")
                        self.logger.debug(f"  From: {source_path}")
                        self.logger.debug(f"  To:   {destination_path}")
                        self.logger.debug(f"  Size: {file_size} bytes")
                        self.copied_files.add(str(source_path))
                        return True
                    else:
                        raise OSError("Copy operation did not complete as expected")
                
                except (OSError, PermissionError) as e:
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        self.logger.warning(f"Copy attempt {attempt + 1} failed for {source_path}: {e}. Retrying...")
                        continue
                    else:
                        self.logger.error(f"Failed to copy {source_path} after {MAX_RETRY_ATTEMPTS} attempts: {e}")
                        return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error copying {source_path}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get file movement statistics.
        
        Returns:
            Dictionary containing movement statistics
        """
        return {
            'files_processed': len(self.copied_files),
            'dry_run_mode': self.dry_run,
            'input_folder': str(self.input_folder),
            'output_folder': str(self.output_folder),
            'scan_nested': self.scan_nested,
            'conflict_resolution': self.conflict_resolution,
            'unknown_strategy': self.unknown_strategy
        }
