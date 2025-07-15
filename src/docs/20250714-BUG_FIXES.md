# Bug Fixes Applied

## 1. Fixed Windows File Backup Collision (WinError 183)

**Problem**: Windows doesn't allow renaming to an existing file name
**Location**: `src/photo_organizer/fingerprint.py`
**Fix**: Remove existing backup file before creating new backup

```python
# Before rename, remove existing backup if it exists
if backup_file.exists():
    backup_file.unlink()
self.fingerprint_file.rename(backup_file)
```

## 2. Changed from Move to Copy Operations

**Problem**: Users don't want original files removed from input folder
**Location**: Multiple files
**Fix**: Changed all move operations to copy operations

### Changes Made:
- `file_mover.py`: Renamed `move_file()` to `copy_file()` and updated logic
- `__main__.py`: Updated to call `copy_file()` instead of `move_file()`
- Updated summary statistics from "moved" to "copied"
- Updated all logging messages to reflect copying
- Updated batch scripts to mention copying instead of moving

## 3. Fixed Timestamp Parsing Issues

**Problem**: EXIF timestamps often lack microseconds, showing as zeros
**Location**: `src/photo_organizer/file_mover.py` and `constants.py`
**Fix**: 
- Changed default date format to exclude microseconds: `%Y-%m-%d at %H-%M-%S`
- Added logic to use file hash when microseconds are zero
- Enhanced EXIF parsing to look for sub-second precision fields

## 4. Enhanced Sub-Second Precision Extraction

**Problem**: Missing sub-second precision in timestamps
**Location**: `src/photo_organizer/metadata_parser.py`
**Fix**: Added logic to extract SubSec fields from EXIF data

```python
# Try to get sub-second precision from other fields
subsec_field = f"{field}SubSec"
if subsec_field in file_data and file_data[subsec_field]:
    subsec = int(file_data[subsec_field])
    microseconds = subsec * 1000 if subsec < 1000 else subsec
    creation_date = creation_date.replace(microsecond=microseconds)
```

## Results

✅ **Fixed**: No more WinError 183 file backup collisions
✅ **Fixed**: Original files remain in input folder (copies made to output)
✅ **Fixed**: Cleaner timestamp formatting without zero microseconds
✅ **Improved**: Better EXIF sub-second precision extraction
✅ **Updated**: All documentation and scripts reflect copying behavior

The tool now safely organizes photos by copying them to date-based folders while preserving the originals in the source location.
