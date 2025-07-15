@echo off
REM Quick script to run Photo Organizer on Windows
REM Organizes files from test-in to test-out folder

echo ================================================
echo Photo Organizer - Quick Run Script
echo ================================================
echo.

REM Change to the project root directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if source directory exists
if not exist "src\photo_organizer" (
    echo ERROR: Photo organizer source not found
    echo Make sure you're running this from the project root
    pause
    exit /b 1
)

REM Check if test-in directory exists
if not exist "test-in" (
    echo ERROR: test-in directory not found
    echo Creating empty test-in directory...
    mkdir test-in
    echo Please add some photos/videos to test-in and run again
    pause
    exit /b 1
)

REM Display what we're about to do
echo Source folder: %CD%\test-in
echo Target folder: %CD%\test-out
echo.

REM Ask user if they want to do a dry run first
set /p choice="Do you want to do a DRY RUN first? (y/n): "
if /i "%choice%"=="y" goto dry_run
if /i "%choice%"=="yes" goto dry_run

goto real_run

:dry_run
echo.
echo ================================================
echo RUNNING DRY RUN (no files will be copied)
echo ================================================
echo.

cd src
python -m photo_organizer --input "..\test-in" --output "..\test-out" --dry-run -vvv

if errorlevel 1 (
    echo.
    echo ERROR: Dry run failed
    cd ..
    pause
    exit /b 1
)

echo.
echo Dry run completed successfully!
echo.
set /p choice2="Do you want to run for REAL now? (y/n): "
if /i "%choice2%"=="n" goto end
if /i "%choice2%"=="no" goto end

:real_run
echo.
echo ================================================
echo RUNNING FOR REAL (files will be copied!)
echo ================================================
echo.

cd src
python -m photo_organizer --input "..\test-in" --output "..\test-out" -vvv

if errorlevel 1 (
    echo.
    echo ERROR: Organizer failed
    cd ..
    pause
    exit /b 1
)

echo.
echo ================================================
echo Organization completed successfully!
echo ================================================
echo.
echo Check the test-out folder for your organized files.

cd ..

:end
echo.
pause
