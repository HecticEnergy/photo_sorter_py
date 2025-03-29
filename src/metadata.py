from PIL import Image
from PIL.ExifTags import TAGS

def get_image_metadata(file_path):
    """Extracts the DateTimeOriginal metadata from an image."""
    try:
        image = Image.open(file_path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                decoded_tag = TAGS.get(tag, tag)
                if decoded_tag == "DateTimeOriginal":
                    return value
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {e}")
    return None
