# 📂 Photo & Video Organizer — Project Specification

## 🧭 Objective  
A Python-based tool that streamlines photo and video organization by scanning input directories (including nested folders), extracting metadata, and sorting files into a structured output hierarchy based on creation dates. Designed for cross-platform use, automation contexts, and configurable workflows.

---

## 🔧 Features

- **Metadata Extraction**  
  Uses `ExifTool` and `Pillow` to extract creation timestamps, device info, and file type.

- **Fallback Logic**  
  Falls back to filename parsing if metadata is missing. Optionally uses filesystem `ctime`, or routes to `/unknown/`, preserving original folder path and filename.

- **Duplicate Detection**  
  Identifies and skips duplicates using content-based hashing (e.g., SHA-256).

- **Corrupt File Handling**  
  Detects unreadable or broken files; logs them and moves to `/error/`, preserving source path structure.

- **Folder Structuring**  
  Ignores source layout and organizes output into `YYYY/MM` format.

- **Filename Conflict Resolution**  
  Adds timestamp suffixes to avoid overwriting files with duplicate names.

- **Config Layering**  
  Supports layered config:
  - Defaults
  - JSON config file
  - CLI argument overrides  
  All config values are validated before execution.

- **Execution Modes**  
  - Interactive CLI logging
  - Structured JSON logs for automation workflows

- **Dry-Run Mode**  
  `--dry-run` flag simulates full execution without modifying files.

- **Summary Output**  
  Prints and/or logs session results: counts of moved, skipped, and errored files.

- **Cross-Platform Support**  
  Compatible with Linux (Ubuntu, Alpine), macOS, and Windows.

---

## ⚙️ Configuration & CLI Flags

| Flag         | Description                                   |
|--------------|-----------------------------------------------|
| `--config`   | Path to JSON config file                      |
| `--dry-run`  | Simulate run without modifying any files      |
| `--output`   | Destination folder override                   |
| `--verbose`  | Console logging verbosity control             |

See [Config Spec](#Config-Spec)
---

## 🧪 Requirements

- **Python Version**: 3.9+
- **Dependencies**:
  - `pyexiftool`
  - `Pillow`
  - `pytest`
  - `hashlib`

---

## 📁 Folder Behavior

- **Input**: Recursively scans nested directories
- **Output**: Files are flattened and sorted into `YYYY/MM` folders
- **Unknown Date Strategy**:
  - Option A: Use file `ctime`
  - Option B: Move to `/unknown/` and preserve original path/filename  
  *(Behavior selectable via config)*

---

## 📝 Logging Structure

- **Format**: JSON
- **Content**: Actions taken, skipped files, errors
- **Summary**: Count of moved, skipped, errored files
- **Location**: Configurable via JSON or CLI

---

## 💡 Stretch Goals (Not in MVP)

- GUI wrapper for local use
- Face clustering/grouping
- Cloud sync capabilities
- Perceptual hashing for fuzzy duplicate detection

---

## 📦 Deliverables

- Python CLI script with modular function blocks
- Config validation module
- Logging utility
- Example config JSON file
- Sample input/output folder structure

--- 
## Config Spec
```json
{
  "input_folder": {
    "value": "/path/to/input/folder",
    "description": "Path to the folder containing files to organize.",
    "required": true,
    "validation_regex": "^.*$"
  },
  "output_folder": {
    "value": "/path/to/output/folder",
    "description": "Destination folder for organized files. Supports date placeholders like %Y/%m.",
    "required": true,
    "validation_regex": "^.*$"
  },
  "fingerprint_folder": {
    "value": "/path/to/fingerprint/folder",
    "description": "Folder to store hash fingerprints for duplicate detection.",
    "required": true,
    "validation_regex": "^.*$"
  },
  "date_format": {
    "value": "%Y-%m-%d at %H-%M-%S (%f)",
    "description": "Customizable format for file naming, using valid placeholders.",
    "required": true,
    "validation_regex": "^.*(%Y|%m|%d|%H|%M|%S|%f).*$"
  },
  "log_path": {
    "value": "/path/to/logs/organize.log",
    "description": "Path to the log file for recording events and errors.",
    "required": false,
    "validation_regex": "^.*\\.log$"
  },
  "log_mode": {
    "value": "file",
    "description": "Set to 'file' for automated logging or 'console' for interactive mode.",
    "required": false,
    "validation_regex": "^(file|console)$"
  },
  "dry_run": {
    "value": false,
    "description": "If true, simulates execution without moving files.",
    "required": false,
    "validation_regex": "^(true|false)$"
  },
  "unknown_strategy": {
    "value": "route_to_unknown",
    "description": "Determines fallback behavior for missing metadata. Options: 'route_to_unknown', 'use_ctime'.",
    "required": false,
    "validation_regex": "^(route_to_unknown|use_ctime)$"
  },
  "scan_nested": {
    "value": true,
    "description": "If true, scans subdirectories within the input folder.",
    "required": false,
    "validation_regex": "^(true|false)$"
  },
  "hash_algorithm": {
    "value": "sha256",
    "description": "Algorithm for generating file fingerprints. Options: 'sha256', 'md5'.",
    "required": false,
    "validation_regex": "^(sha256|md5)$"
  },
  "filename_conflict_resolution": {
    "value": "timestamp_suffix",
    "description": "Strategy for resolving duplicate filenames. Options: 'timestamp_suffix', 'uuid_suffix'.",
    "required": false,
    "validation_regex": "^(timestamp_suffix|uuid_suffix)$"
  }
}
```