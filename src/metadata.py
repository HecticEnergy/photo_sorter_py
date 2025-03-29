import exiftool
import os

# Define supported file extensions
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif", ".heic", ".heif", ".raw"}
SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".3gp", ".webm"}

def check_supported_format(file_path):
    """Checks if the file has a supported format for metadata extraction."""
    _, file_extension = os.path.splitext(file_path.lower())
    if file_extension in SUPPORTED_IMAGE_FORMATS or file_extension in SUPPORTED_VIDEO_FORMATS:
        return True
    print(f"Unsupported file format: {file_path}")
    return False

def get_image_metadata(file_path):
    """Extracts the DateTimeOriginal metadata from an image."""
    try:
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(file_path)
            # Extract 'DateTimeOriginal' field from the metadata
            date_time_original = metadata.get("EXIF:DateTimeOriginal")
            if date_time_original:
                return date_time_original
    except Exception as e:
        print(f"Error reading image metadata from {file_path}: {e}")
    return None

def get_video_metadata(file_path):
    """Extracts the creation date metadata from a video."""
    try:
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(file_path)
            # Extract 'CreateDate' field from the metadata
            create_date = metadata.get("QuickTime:CreateDate") or metadata.get("MediaCreateDate")
            if create_date:
                return create_date
    except Exception as e:
        print(f"Error reading video metadata from {file_path}: {e}")
    return None
