# Product Requirements Document (PRD)

## Product Name
Photo and Video Organizer

## Purpose
A Python-based tool to automatically organize photos and videos into structured folders based on metadata (e.g., creation dates), supporting both interactive and automated (scheduled) usage.

## Target Users
- 

## Features

### 1. Metadata Extraction
- Extract metadata from images and videos using ExifTool and Pillow.
- Use metadata (e.g., creation date) to determine file organization.

### 2. File Organization
- Move/copy files into a configurable folder hierarchy (e.g., `YYYY/MM`).
- Support custom date formats for folder and file naming.

### 3. Duplicate Detection
- Use SHA-256 hashing to detect and skip duplicate files.
- Store fingerprints in a dedicated folder for future reference.

### 4. Logging
- Centralized logging system.
- Support logging to console (for CLI use) or to a file (for scheduled/automated tasks).
- Log key events: metadata extraction, duplicate detection, errors.

### 5. Configuration
- All settings configurable via a JSON file (`settings/config.json`).
- Configurable options: input folder, output folder, fingerprint folder, date format, log path, log mode.

### 6. Cross-Platform Support
- Must work on Windows, macOS, and Linux.

### 7. Command-Line and Automation
- Usable interactively via CLI.
- Can be run as a scheduled task (e.g., cron job, Windows Task Scheduler).

### 8. Testing
- Unit tests for core modules using pytest.

## Non-Functional Requirements
- Python 3.9+ required.
- Dependencies: pyexiftool, Pillow, pytest, hashlib.
- Must handle large numbers of files efficiently.
- Must not modify original files unless explicitly configured.

## Out of Scope
- Cloud storage integration.
- GUI (Graphical User Interface).

## Success Criteria
- Files are organized correctly by date.
- No duplicates in the output folder.
- Logs are accurate and useful for debugging.
- Easy to configure and run on all major OSes.