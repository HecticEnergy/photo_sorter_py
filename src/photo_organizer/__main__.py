#!/usr/bin/env python3
"""
Main entry point for Photo Organizer.

This module provides the CLI interface and orchestrates the photo organization process.
Can be run as: python -m photo_organizer
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .config_loader import ConfigLoader
from .metadata_parser import MetadataParser
from .fingerprint import FingerprintManager
from .file_mover import FileMover
from .logger import Logger
from .validator import ConfigValidator


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="photo_organizer",
        description="Organize photos and videos by metadata into date-based folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  photo_organizer --config organize.json
  photo_organizer --config organize.json --dry-run
  python -m photo_organizer --input /photos --output /sorted --dry-run
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to JSON configuration file"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input folder containing photos/videos to organize"
    )
    
    parser.add_argument(
        "--output", "-o", 
        type=str,
        help="Output folder for organized files"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Simulate the organization without moving files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase logging verbosity (use -v, -vv, -vvv)"
    )
    
    parser.add_argument(
        "--log-mode",
        choices=["console", "file", "both"],
        default="console",
        help="Logging output mode"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def load_and_validate_config(config_path: Optional[str], cli_args: Dict[str, Any]) -> Dict[str, Any]:
    """Load configuration from file and CLI arguments, then validate."""
    try:
        # Load base config
        config_loader = ConfigLoader()
        if config_path:
            config = config_loader.load_from_file(config_path)
        else:
            config = config_loader.get_default_config()
            
        # Override with CLI arguments
        config = config_loader.merge_cli_args(config, cli_args)
        
        # Validate final configuration
        validator = ConfigValidator()
        validation_result = validator.validate(config)
        
        if not validation_result.is_valid:
            print("Configuration validation failed:", file=sys.stderr)
            for error in validation_result.errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
            
        return config
        
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)


def run_organization(config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the photo organization process."""
    # Initialize components
    logger = Logger(config)
    metadata_parser = MetadataParser(config, logger)
    fingerprint_manager = FingerprintManager(config, logger)
    file_mover = FileMover(config, logger)
    
    logger.info("Starting photo organization process")
    logger.info(f"Input folder: {config['input_folder']}")
    logger.info(f"Output folder: {config['output_folder']}")
    logger.info(f"Dry run mode: {config.get('dry_run', False)}")
    
    try:
        # Initialize fingerprint manager
        fingerprint_manager.load_existing_fingerprints()
        
        # Scan input directory
        input_path = Path(config['input_folder'])
        if not input_path.exists():
            raise FileNotFoundError(f"Input folder does not exist: {input_path}")
            
        # Process files
        summary = {
            "copied": 0,
            "skipped": 0,
            "duplicates": 0,
            "errors": 0,
            "unknown": 0
        }
        
        # Track all operations for final summary
        operations_log = []
        
        for file_path in file_mover.scan_files(input_path):
            try:
                logger.debug(f"Processing file: {file_path}")
                
                # Extract metadata
                metadata = metadata_parser.extract_metadata(file_path)
                
                # Check for duplicates
                file_hash = fingerprint_manager.calculate_hash(file_path)
                if fingerprint_manager.is_duplicate(file_hash, file_path):
                    logger.info(f"Duplicate file skipped: {file_path}")
                    summary["duplicates"] += 1
                    # Track operation for summary
                    operations_log.append({
                        "source": str(file_path),
                        "destination": "N/A",
                        "status": "duplicate"
                    })
                    continue
                    
                # Determine destination
                destination = file_mover.determine_destination(file_path, metadata)
                
                # Log the operation details
                if config.get('dry_run', False):
                    logger.info("[DRY RUN] Would copy:")
                    logger.info(f"  From: {file_path}")
                    logger.info(f"  To:   {destination}")
                else:
                    logger.info("Copying:")
                    logger.info(f"  From: {file_path}")
                    logger.info(f"  To:   {destination}")
                
                # Copy file (or simulate in dry-run mode)
                if file_mover.copy_file(file_path, destination):
                    fingerprint_manager.record_fingerprint(file_hash, destination)
                    summary["copied"] += 1
                    # Track operation for summary
                    operations_log.append({
                        "source": str(file_path),
                        "destination": str(destination),
                        "status": "copied"
                    })
                    if not config.get('dry_run', False):
                        logger.info(f"✓ Successfully copied to: {destination}")
                else:
                    summary["skipped"] += 1
                    # Track operation for summary
                    operations_log.append({
                        "source": str(file_path),
                        "destination": str(destination),
                        "status": "failed"
                    })
                    logger.warning(f"✗ Failed to copy: {file_path}")
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                summary["errors"] += 1
                # Track operation for summary
                operations_log.append({
                    "source": str(file_path),
                    "destination": "N/A",
                    "status": "error",
                    "error": str(e)
                })
                
        # Save fingerprints
        fingerprint_manager.save_fingerprints()
        
        # Display detailed summary
        logger.info("=" * 60)
        logger.info("ORGANIZATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files copied: {summary['copied']}")
        logger.info(f"Files skipped (duplicates): {summary['duplicates']}")
        logger.info(f"Files skipped (other): {summary['skipped']}")
        logger.info(f"Files with errors: {summary['errors']}")
        logger.info(f"Files with unknown dates: {summary['unknown']}")
        logger.info(f"Total files processed: {sum(summary.values())}")
        
        # Show detailed operations if requested or if there are few files
        if len(operations_log) <= 10 or config.get('verbose', False):
            logger.info("\nDETAILED OPERATIONS:")
            logger.info("-" * 40)
            for i, op in enumerate(operations_log, 1):
                status_indicator = {
                    'copied': '✓',
                    'duplicate': '⚠',
                    'failed': '✗',
                    'error': '✗'
                }.get(op['status'], '?')
                
                logger.info(f"{i:3d}. {status_indicator} {op['status'].upper()}")
                logger.info(f"      From: {op['source']}")
                if op['destination'] != 'N/A':
                    logger.info(f"      To:   {op['destination']}")
                if 'error' in op:
                    logger.info(f"      Error: {op['error']}")
                logger.info("")
        elif len(operations_log) > 10:
            logger.info(f"\n(Use --verbose to see all {len(operations_log)} operations)")
        
        logger.info("=" * 60)
        logger.info("Organization process completed")
        logger.info(f"Summary: {summary}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Organization process failed: {e}")
        raise


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Convert args to dict for easier handling
    cli_args = {
        "input_folder": args.input,
        "output_folder": args.output,
        "dry_run": args.dry_run,
        "log_mode": args.log_mode,
        "verbose": args.verbose
    }
    
    # Remove None values
    cli_args = {k: v for k, v in cli_args.items() if v is not None}
    
    try:
        # Load and validate configuration
        config = load_and_validate_config(args.config, cli_args)
        
        # Run organization process
        summary = run_organization(config)
        
        # Output summary
        print(json.dumps({
            "status": "complete",
            "summary": summary
        }, indent=2))
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
