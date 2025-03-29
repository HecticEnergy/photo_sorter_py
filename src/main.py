import os
from src.organizer import organize_files
from src.settings import ParserSettings

def main(settings=None):
    """Main function to manage the workflow."""
    try:
        # If no settings are provided, attempt to load settings from the configuration file
        if settings is None:
            print("No settings provided. Attempting to load settings from the configuration file...")
            settings = load_settings()  

        # Validate the settings
        settings.validate()

        # Ensure the fingerprint folder exists
        if not os.path.exists(settings.fingerprint_folder()):
            os.makedirs(settings.fingerprint_folder())

        # Start organizing files
        organize_files(settings)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
