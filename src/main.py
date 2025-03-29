import os
from src.organizer import organize_files
from src.settings import ParserSettings

def main(settings):
    """Main function to manage the workflow."""
    settings.validate()  # Validate settings before proceeding
    if not os.path.exists(settings.fingerprint_folder()):
        os.makedirs(settings.fingerprint_folder())
    organize_files(settings)

if __name__ == "__main__":
    parser_settings = ParserSettings(
        input_folder="/path/to/input/folder",  # Update with your actual input folder
        output_folder="/path/to/output/folder",  # Update with your actual output folder
        fingerprint_folder="/path/to/settings",  # Folder for storing fingerprints
        date_format="%Y-%m-%d at %H-%M-%S (%f)"  # Custom filename format
    )
    main(parser_settings)
