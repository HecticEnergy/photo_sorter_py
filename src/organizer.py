import os
import shutil
from datetime import datetime
from src.file_utils import create_fingerprint, is_duplicate
from src.metadata import get_image_metadata, get_video_metadata, check_supported_format
from src.logging import log_message  # Import log_message for logging

def create_folder_structure(base_folder, date):
    """Creates a folder structure based on the custom format."""
    folder_path = os.path.join(base_folder, date.strftime("%Y/%m"))
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def generate_filename(date, date_format):
    """Generates a filename based on the custom format."""
    return date.strftime(date_format)[:-3]  # Trim milliseconds for precision

def copy_file_to_folder(file_path, folder_path, filename):
    """Copies a file to the specified folder with a custom filename."""
    new_file_path = os.path.join(folder_path, f"{filename}{os.path.splitext(file_path)[-1]}")
    shutil.copy2(file_path, new_file_path)  # Preserve metadata
    log_message("info", f"Copied {file_path} to {new_file_path}")

def process_file(file_path, settings):
    """Processes a single file: extracts metadata, creates folder, fingerprints, and copies."""
    fingerprint_folder = settings.fingerprint_folder()
    output_folder = settings.output_folder()

    # Check if the file format is supported
    if not check_supported_format(file_path):
        log_message("warning", f"Unsupported format: {file_path}. Skipping.")
        return

    # Check for duplicates
    if is_duplicate(file_path, fingerprint_folder):
        log_message("warning", f"Duplicate detected: {file_path}. Skipping processing.")
        return

    # Determine metadata and process accordingly
    metadata = None
    if file_path.lower().endswith(tuple(settings.SUPPORTED_IMAGE_FORMATS)):
        metadata = get_image_metadata(file_path)
    elif file_path.lower().endswith(tuple(settings.SUPPORTED_VIDEO_FORMATS)):
        metadata = get_video_metadata(file_path)

    if metadata:
        try:
            # Parse the date string into a datetime object
            date = datetime.strptime(metadata, "%Y:%m:%d %H:%M:%S")
            # Create the folder structure based on the date
            folder_path = create_folder_structure(output_folder, date)
            # Generate the filename
            filename = generate_filename(date, settings.date_format())
            # Copy the file to the destination
            copy_file_to_folder(file_path, folder_path, filename)
            # Create a fingerprint for the processed file
            create_fingerprint(file_path, fingerprint_folder)
        except ValueError as e:
            log_message("error", f"Invalid date format in metadata for {file_path}: {e}")
    else:
        log_message("warning", f"No metadata found for {file_path}. Skipping.")

def organize_files(settings):
    """Organizes files by reading metadata and arranging them into folders."""
    input_folder = settings.input_folder()
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path, settings)
