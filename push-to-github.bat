@echo off
echo ================================================
echo    Pushing Playlist Downloader to GitHub
echo ================================================

echo.
echo Checking git status...
git status

echo.
echo Adding all files to git...
git add .

echo.
echo Committing changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message="Deploy playlist downloader to production"

git commit -m "%commit_message%"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ================================================
echo    Push completed successfully!
echo ================================================
echo.
echo Next steps:
echo 1. Go to your Savella dashboard
echo 2. Connect your GitHub repository
echo 3. Set environment variables:
echo    - SPOTIFY_CLIENT_ID
echo    - SPOTIFY_CLIENT_SECRET
echo 4. Deploy the application
echo.
echo Your app will be available at your Savella domain!
echo ================================================

pause
