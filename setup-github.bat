@echo off
echo ================================================
echo    GitHub Repository Setup for Savella
echo ================================================

echo.
echo This script will help you set up your GitHub repository for Savella deployment.
echo.

echo Step 1: Initialize Git Repository
echo ---------------------------------
if not exist ".git" (
    echo Initializing new git repository...
    git init
    git branch -M main
) else (
    echo Git repository already exists.
)

echo.
echo Step 2: Create GitHub Repository
echo ---------------------------------
echo Please create a new repository on GitHub:
echo 1. Go to https://github.com/new
echo 2. Name it: playlist-downloader
echo 3. Make it public or private (your choice)
echo 4. Do NOT initialize with README (we have our own files)
echo 5. Copy the repository URL

echo.
set /p repo_url="Enter your GitHub repository URL (https://github.com/username/playlist-downloader.git): "

if "%repo_url%"=="" (
    echo Error: Repository URL is required!
    pause
    exit /b 1
)

echo.
echo Step 3: Configure Git Remote
echo ----------------------------
echo Adding GitHub remote...
git remote remove origin 2>nul
git remote add origin %repo_url%

echo.
echo Step 4: Stage All Files
echo ----------------------
echo Adding all files to git...
git add .

echo.
echo Step 5: Initial Commit
echo ---------------------
echo Creating initial commit...
git commit -m "Initial commit - Spotify/YouTube Playlist Downloader for Savella deployment"

echo.
echo Step 6: Push to GitHub
echo ---------------------
echo Pushing to GitHub...
git push -u origin main

echo.
echo ================================================
echo    GitHub Setup Complete!
echo ================================================
echo.
echo Next steps for Savella deployment:
echo.
echo 1. Go to your Savella dashboard
echo 2. Click "New Project"
echo 3. Select "Import from GitHub"
echo 4. Choose: playlist-downloader
echo 5. Set environment variables:
echo    - SPOTIFY_CLIENT_ID
echo    - SPOTIFY_CLIENT_SECRET
echo 6. Deploy!
echo.
echo Your repository: %repo_url%
echo ================================================

pause
