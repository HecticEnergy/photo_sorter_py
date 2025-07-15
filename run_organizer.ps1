# Quick PowerShell script to run Photo Organizer on Windows
# Organizes files from test-in to test-out folder

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Photo Organizer - Quick Run Script (PowerShell)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if source directory exists
if (-not (Test-Path "src\photo_organizer")) {
    Write-Host "ERROR: Photo organizer source not found" -ForegroundColor Red
    Write-Host "Make sure you're running this from the project root" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if test-in directory exists
if (-not (Test-Path "test-in")) {
    Write-Host "ERROR: test-in directory not found" -ForegroundColor Red
    Write-Host "Creating empty test-in directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "test-in" -Force | Out-Null
    Write-Host "Please add some photos/videos to test-in and run again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Display what we're about to do
$sourceFolder = Join-Path $PWD "test-in"
$targetFolder = Join-Path $PWD "test-out"

Write-Host "Source folder: $sourceFolder" -ForegroundColor Yellow
Write-Host "Target folder: $targetFolder" -ForegroundColor Yellow
Write-Host ""

# Count files in test-in
$fileCount = (Get-ChildItem -Path "test-in" -Recurse -File | Where-Object { 
    $_.Extension -match '\.(jpg|jpeg|png|tiff|tif|bmp|gif|webp|heic|heif|raw|cr2|nef|arw|dng|orf|mp4|avi|mov|mkv|wmv|flv|webm|m4v|3gp|mts|m2ts|ts|vob|asf|rm|rmvb)$' 
}).Count

Write-Host "Found $fileCount supported media files in test-in" -ForegroundColor Cyan
Write-Host ""

# Ask user if they want to do a dry run first
$choice = Read-Host "Do you want to do a DRY RUN first? (y/n)"

if ($choice -match '^[Yy]') {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Magenta
    Write-Host "RUNNING DRY RUN (no files will be copied)" -ForegroundColor Magenta
    Write-Host "================================================" -ForegroundColor Magenta
    Write-Host ""
    
    Set-Location "src"
    $result = python -m photo_organizer --input "..\test-in" --output "..\test-out" --dry-run --verbose
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Dry run failed" -ForegroundColor Red
        Set-Location ".."
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "Dry run completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    $choice2 = Read-Host "Do you want to run for REAL now? (y/n)"
    if ($choice2 -notmatch '^[Yy]') {
        Set-Location ".."
        Write-Host "Operation cancelled by user." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 0
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Red
Write-Host "RUNNING FOR REAL (files will be copied!)" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Red
Write-Host ""

# Ensure we're in src directory
if ((Get-Location).Path -notlike "*\src") {
    Set-Location "src"
}

# Run the actual organization
$result = python -m photo_organizer --input "..\test-in" --output "..\test-out" --verbose

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Organizer failed" -ForegroundColor Red
    Set-Location ".."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Organization completed successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Check the test-out folder for your organized files." -ForegroundColor Green

Set-Location ".."

# Show results if test-out was created
if (Test-Path "test-out") {
    Write-Host ""
    Write-Host "Organized folder structure:" -ForegroundColor Cyan
    Get-ChildItem -Path "test-out" -Recurse -Directory | ForEach-Object {
        $relativePath = $_.FullName.Replace($PWD, ".")
        Write-Host "  $relativePath" -ForegroundColor Gray
    }
    
    $organizedCount = (Get-ChildItem -Path "test-out" -Recurse -File).Count
    Write-Host ""
    Write-Host "Total files organized: $organizedCount" -ForegroundColor Green
}

Write-Host ""
Read-Host "Press Enter to exit"
