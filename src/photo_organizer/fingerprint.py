"""
File fingerprinting and duplicate detection for Photo Organizer.

This module handles generating file hashes, storing fingerprints,
and detecting duplicate files to prevent redundant processing.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Set

from .constants import HashAlgorithm, FILE_BUFFER_SIZE, HASH_BUFFER_SIZE


class FingerprintManager:
    """Manages file fingerprints for duplicate detection."""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize the fingerprint manager.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance for recording operations
        """
        self.config = config
        self.logger = logger
        self.fingerprint_folder = Path(config.get('fingerprint_folder', 'fingerprints'))
        self.hash_algorithm = config.get('hash_algorithm', HashAlgorithm.SHA256.value)
        self.duplicate_strategy = config.get('duplicate_strategy', 'skip')
        
        # In-memory fingerprint database
        self.fingerprints: Dict[str, Dict[str, Any]] = {}
        self.fingerprint_file = self.fingerprint_folder / f'fingerprints_{self.hash_algorithm}.json'
        
        # Initialize fingerprint directory
        self._ensure_fingerprint_directory()
    
    def _ensure_fingerprint_directory(self) -> None:
        """Create fingerprint directory if it doesn't exist."""
        try:
            self.fingerprint_folder.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Fingerprint directory ready: {self.fingerprint_folder}")
        except Exception as e:
            self.logger.error(f"Failed to create fingerprint directory {self.fingerprint_folder}: {e}")
            raise
    
    def calculate_hash(self, file_path: Path) -> Optional[str]:
        """
        Calculate hash for a file.
        
        Args:
            file_path: Path to the file to hash
            
        Returns:
            Hex string of the file hash, or None if error occurred
        """
        try:
            # Choose hash algorithm
            if self.hash_algorithm == HashAlgorithm.MD5.value:
                hasher = hashlib.md5()
            elif self.hash_algorithm == HashAlgorithm.SHA1.value:
                hasher = hashlib.sha1()
            else:  # Default to SHA256
                hasher = hashlib.sha256()
            
            # Read and hash file in chunks
            with open(file_path, 'rb') as f:
                while chunk := f.read(HASH_BUFFER_SIZE):
                    hasher.update(chunk)
            
            file_hash = hasher.hexdigest()
            self.logger.debug(f"Calculated {self.hash_algorithm} hash for {file_path}: {file_hash[:16]}...")
            return file_hash
            
        except Exception as e:
            self.logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return None
    
    def is_duplicate(self, file_hash: str, file_path: Path) -> bool:
        """
        Check if a file is a duplicate based on its hash.
        
        Args:
            file_hash: Hash of the file to check
            file_path: Path to the file being checked
            
        Returns:
            True if file is a duplicate, False otherwise
        """
        if not file_hash:
            return False
        
        if file_hash in self.fingerprints:
            existing_entry = self.fingerprints[file_hash]
            existing_path = existing_entry.get('path')
            
            # Check if the existing file still exists
            if existing_path and Path(existing_path).exists():
                self.logger.debug(f"Duplicate detected: {file_path} matches {existing_path}")
                return True
            else:
                # Remove stale fingerprint
                self.logger.debug(f"Removing stale fingerprint for {existing_path}")
                del self.fingerprints[file_hash]
        
        return False
    
    def record_fingerprint(self, file_hash: str, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a file fingerprint in the database.
        
        Args:
            file_hash: Hash of the file
            file_path: Path to the file
            metadata: Optional metadata to store with the fingerprint
        """
        if not file_hash:
            return
        
        entry = {
            'path': str(file_path),
            'timestamp': file_path.stat().st_mtime if file_path.exists() else None,
            'size': file_path.stat().st_size if file_path.exists() else None,
            'algorithm': self.hash_algorithm,
            'metadata': metadata or {}
        }
        
        self.fingerprints[file_hash] = entry
        self.logger.debug(f"Recorded fingerprint for {file_path}")
    
    def load_existing_fingerprints(self) -> None:
        """Load existing fingerprints from the database file."""
        if not self.fingerprint_file.exists():
            self.logger.debug("No existing fingerprint database found")
            return
        
        try:
            with open(self.fingerprint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and load fingerprints
            if isinstance(data, dict) and 'fingerprints' in data:
                self.fingerprints = data['fingerprints']
                self.logger.info(f"Loaded {len(self.fingerprints)} existing fingerprints")
                
                # Clean up stale entries
                self._cleanup_stale_fingerprints()
            else:
                self.logger.warning("Invalid fingerprint database format, starting fresh")
                self.fingerprints = {}
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse fingerprint database: {e}")
            self.fingerprints = {}
        except Exception as e:
            self.logger.error(f"Failed to load fingerprint database: {e}")
            self.fingerprints = {}
    
    def _cleanup_stale_fingerprints(self) -> None:
        """Remove fingerprints for files that no longer exist."""
        stale_hashes = []
        
        for file_hash, entry in self.fingerprints.items():
            file_path = Path(entry.get('path', ''))
            if not file_path.exists():
                stale_hashes.append(file_hash)
        
        for file_hash in stale_hashes:
            del self.fingerprints[file_hash]
        
        if stale_hashes:
            self.logger.info(f"Removed {len(stale_hashes)} stale fingerprints")
    
    def save_fingerprints(self) -> None:
        """Save fingerprints to the database file."""
        try:
            database_data = {
                'version': '1.0',
                'algorithm': self.hash_algorithm,
                'fingerprint_count': len(self.fingerprints),
                'fingerprints': self.fingerprints
            }
            
            # Create backup if file exists
            if self.fingerprint_file.exists():
                backup_file = self.fingerprint_file.with_suffix('.json.bak')
                self.fingerprint_file.rename(backup_file)
                self.logger.debug(f"Created backup: {backup_file}")
            
            # Write new fingerprint database
            with open(self.fingerprint_file, 'w', encoding='utf-8') as f:
                json.dump(database_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved {len(self.fingerprints)} fingerprints to {self.fingerprint_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save fingerprint database: {e}")
            
            # Restore backup if save failed
            backup_file = self.fingerprint_file.with_suffix('.json.bak')
            if backup_file.exists():
                try:
                    backup_file.rename(self.fingerprint_file)
                    self.logger.info("Restored fingerprint database from backup")
                except Exception as restore_error:
                    self.logger.error(f"Failed to restore backup: {restore_error}")
    
    def get_duplicate_groups(self) -> Dict[str, list]:
        """
        Get groups of duplicate files organized by hash.
        
        Returns:
            Dictionary mapping hashes to lists of file paths
        """
        duplicate_groups = {}
        
        for file_hash, entry in self.fingerprints.items():
            file_path = Path(entry.get('path', ''))
            if file_path.exists():
                if file_hash not in duplicate_groups:
                    duplicate_groups[file_hash] = []
                duplicate_groups[file_hash].append(str(file_path))
        
        # Filter to only groups with multiple files
        return {k: v for k, v in duplicate_groups.items() if len(v) > 1}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get fingerprint database statistics.
        
        Returns:
            Dictionary containing database statistics
        """
        total_fingerprints = len(self.fingerprints)
        existing_files = 0
        total_size = 0
        
        for entry in self.fingerprints.values():
            file_path = Path(entry.get('path', ''))
            if file_path.exists():
                existing_files += 1
                try:
                    total_size += file_path.stat().st_size
                except OSError:
                    pass
        
        duplicate_groups = self.get_duplicate_groups()
        total_duplicates = sum(len(group) for group in duplicate_groups.values())
        
        return {
            'total_fingerprints': total_fingerprints,
            'existing_files': existing_files,
            'stale_fingerprints': total_fingerprints - existing_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'duplicate_groups': len(duplicate_groups),
            'total_duplicates': total_duplicates,
            'algorithm': self.hash_algorithm
        }
    
    def export_report(self, output_path: Path) -> None:
        """
        Export a detailed fingerprint report.
        
        Args:
            output_path: Path to save the report
        """
        try:
            stats = self.get_statistics()
            duplicate_groups = self.get_duplicate_groups()
            
            report = {
                'generated_at': str(Path().cwd()),
                'statistics': stats,
                'duplicate_groups': duplicate_groups,
                'all_fingerprints': {
                    hash_val: {
                        'path': entry.get('path'),
                        'exists': Path(entry.get('path', '')).exists(),
                        'size': entry.get('size'),
                        'timestamp': entry.get('timestamp')
                    }
                    for hash_val, entry in self.fingerprints.items()
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Fingerprint report exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export fingerprint report: {e}")
    
    def verify_file_integrity(self, file_path: Path, expected_hash: str) -> bool:
        """
        Verify that a file's current hash matches the expected hash.
        
        Args:
            file_path: Path to the file to verify
            expected_hash: Expected hash value
            
        Returns:
            True if hashes match, False otherwise
        """
        current_hash = self.calculate_hash(file_path)
        if current_hash == expected_hash:
            self.logger.debug(f"File integrity verified: {file_path}")
            return True
        else:
            self.logger.warning(f"File integrity mismatch for {file_path}: expected {expected_hash[:16]}..., got {current_hash[:16] if current_hash else 'None'}...")
            return False
