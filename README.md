# Photo and Video Organizer

> [!CAUTION] USE AT YOUR OWN RISK
> This entire project was *vibe coded* with copilot.

A Python-based tool to automatically organize photos and videos into structured folders based on metadata, such as creation dates. This project is designed to streamline file organization while supporting both command-line usage and automated tasks like scheduled jobs.

---

## Features
- **Metadata Extraction**: Uses ExifTool and Pillow for robust image and video metadata extraction.
- **Flexible Execution Modes**: Supports logging to the console for interactive CLI use or to a file for scheduled automation tasks.
- **Duplicate Detection**: Identifies and skips duplicate files using content hashing.
- **Configurable Folder Structure**: Automatically organizes files into a structured hierarchy (e.g., `YYYY/MM`).
- **Cross-Platform**: Works on Windows, macOS, and Linux environments.

---

## Requirements
- **Python**: Version 3.9 or later
- **Dependencies**:
  - `pyexiftool`
  - `Pillow`
  - `pytest`
  - `hashlib`

---

## Installation

### Install Python Dependencies
1. Clone the repository:
   ```bash
   git clone https://github.com/HecticEnergy/photo_sorter_py.git
   cd photo-video-organizer
   ```

2. Install dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. Install ExifTool:
   - **Linux**:
     ```bash
     sudo apt install exiftool
     ```
   - **macOS**:
     ```bash
     brew install exiftool
     ```
   - **Windows**:
     Download and install from [ExifTool's official site](https://exiftool.org/).

---

## Usage

### Running from the Command Line
Run the tool interactively from the command line:
```bash
python src/main.py --mode console
```

### Scheduled Tasks
To automate the tool via a scheduled task (e.g., a cron job on Linux):
1. Use the `--mode scheduled` flag:
   ```bash
   python src/main.py --mode scheduled
   ```
2. Set up a cron job or task scheduler to run the script periodically:
   - Example for Linux:
     ```bash
     0 0 * * * /usr/bin/python3 /path/to/src/main.py --mode scheduled
     ```

---

## Configuration
The project is configurable via the `./settings/config.json` file.

### Sample `config.json`:
```json
{
    "input_folder": "/path/to/input/folder",
    "output_folder": "/path/to/output/folder",
    "fingerprint_folder": "/path/to/fingerprint/folder",
    "date_format": "%Y-%m-%d at %H-%M-%S (%f)",
    "log_path": "/path/to/logs/organize.log",
    "log_mode": "file"
}
```

- **`input_folder`**: Path to the folder containing files to organize.
- **`output_folder`**: Path to the destination folder where organized files will be stored.
- **`fingerprint_folder`**: Folder to store fingerprints for duplicate detection.
- **`date_format`**: Customizable format for naming files and folders.
- **`log_path`**: Path to the log file.
- **`log_mode`**: Either `"console"` for interactive mode or `"file"` for logging in automated tasks.

---

## Features in Detail

### Logging
Centralized logging powered by the `logging.py` module:
- Logs can be directed to the console (`log_mode: console`) or to a file (`log_mode: file`).
- Tracks key events such as metadata extraction, duplicate detection, and errors.

### Duplicate Detection
Uses SHA-256 hashing to create fingerprints for files. If a file has already been processed, it will be skipped automatically.

---

## Development

### Codebase Overview
- **`src/main.py`**: Entry point for the script. Determines execution mode (CLI or scheduled).
- **`src/settings.py`**: Manages configuration settings.
- **`src/logging.py`**: Handles centralized logging for the project.
- **`src/metadata.py`**: Extracts metadata from images and videos.
- **`src/file_utils.py`**: Performs file operations such as fingerprint creation and duplicate detection.
- **`src/organizer.py`**: Core logic for organizing files based on metadata.

### Running Tests
Tests are implemented using `pytest`. Run all tests with:
```bash
pytest
```

---

## Contribution
Contributions are welcome! Please open an issue or pull request for bug fixes or new features.

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Describe your feature/fix here"
   ```
4. Push your branch and open a pull request.

---

## License
This project is licensed under the [GNU v3](LICENSE).

---

## Acknowledgments
- [ExifTool](https://exiftool.org/): Used for extracting metadata from files.
- [Pillow](https://python-pillow.org/): Python Imaging Library for handling images.

