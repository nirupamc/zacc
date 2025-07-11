@echo off
REM Spotify/YouTube Playlist Downloader Setup Script for Windows

echo 🎵 Setting up Playlist Downloader...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg is not installed.
    echo Please install FFmpeg:
    echo   Using Chocolatey: choco install ffmpeg
    echo   Or download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create directories
echo 📁 Creating directories...
if not exist downloads mkdir downloads
if not exist temp mkdir temp
if not exist output mkdir output

REM Copy environment file if it doesn't exist
if not exist .env (
    echo ⚙️ Creating environment file...
    copy .env.example .env
    echo ✅ Please edit .env file with your configurations
)

echo.
echo 🚀 Setup complete! Run the application with:
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo Then open http://localhost:5000 in your browser
pause
