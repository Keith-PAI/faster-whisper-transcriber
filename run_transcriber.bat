@echo off
echo YouTube Transcript Generator
echo ============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import yt_dlp, whisper" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install yt-dlp openai-whisper
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

echo Starting YouTube Transcript Generator...
python youtube_transcriber.py

pause