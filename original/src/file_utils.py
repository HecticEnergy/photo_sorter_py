import hashlib
import os
import json
from src.logging_wrapper import log_message


def calculate_file_hash(file_path):
    """Calculates a hash of the file's content for fingerprinting."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):  # Read in chunks
                hasher.update(chunk)
    except Exception as e:
        log_message("error", f"Error calculating hash for {file_path}: {e}")
        return None
    log_message("info", f"Calculated hash for file: {file_path}")
    return hasher.hexdigest()


def create_fingerprint(file_path, fingerprint_folder):
    """Creates a fingerprint file in the specified folder."""
    file_hash = calculate_file_hash(file_path)
    if file_hash:
        fingerprint_path = os.path.join(fingerprint_folder, f"{file_hash}.json")
        metadata = {
            "original_path": file_path,
            "file_hash": file_hash,
            "size": os.path.getsize(file_path),
            "modified_time": os.path.getmtime(file_path),
        }
        try:
            os.makedirs(fingerprint_folder, exist_ok=True)
            with open(fingerprint_path, "w") as f:
                json.dump(metadata, f)
            log_message("info", f"Fingerprint created for file: {file_path}")
            return fingerprint_path
        except Exception as e:
            log_message("error", f"Error creating fingerprint for {file_path}: {e}")
    else:
        log_message("warning", f"Failed to create fingerprint for file: {file_path}")
    return None


def is_duplicate(file_path, fingerprint_folder):
    """Checks if the file already exists in the fingerprint folder."""
    file_hash = calculate_file_hash(file_path)
    if file_hash:
        fingerprint_path = os.path.join(fingerprint_folder, f"{file_hash}.json")
        if os.path.exists(fingerprint_path):
            log_message("warning", f"Duplicate detected: {file_path}")
            return True
    log_message("info", f"No duplicate found for file: {file_path}")
    return False
