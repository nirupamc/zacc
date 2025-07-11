@echo off
REM Quick deployment script for Savella (Windows)

echo 🚀 Preparing Playlist Downloader for Savella deployment...

REM Clean up development files
echo 🧹 Cleaning up development files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

REM Clear download directories
if exist downloads rmdir /s /q downloads
if exist temp rmdir /s /q temp
if exist output rmdir /s /q output
if exist logs rmdir /s /q logs

REM Create necessary directories
mkdir downloads temp output logs

REM Create deployment package (requires 7-Zip or similar)
echo 📦 Creating deployment archive...
if exist "C:\Program Files\7-Zip\7z.exe" (
    "C:\Program Files\7-Zip\7z.exe" a -ttar playlist-downloader-savella.tar . -x!.git -x!*.tar -x!__pycache__ -x!*.pyc
    "C:\Program Files\7-Zip\7z.exe" a -tgzip playlist-downloader-savella.tar.gz playlist-downloader-savella.tar
    del playlist-downloader-savella.tar
    echo ✅ Deployment archive created: playlist-downloader-savella.tar.gz
) else (
    echo ⚠️ 7-Zip not found. Please create archive manually or install 7-Zip
    echo Include all files except: .git, __pycache__, *.pyc, downloads/*, temp/*, output/*
)

echo.
echo 📋 Next steps for Savella deployment:
echo 1. Upload the archive to Savella
echo 2. Set environment variables:
echo    - SECRET_KEY (generate a strong one)
echo    - SPOTIFY_CLIENT_ID
echo    - SPOTIFY_CLIENT_SECRET
echo 3. Configure domain and SSL
echo 4. Monitor the deployment logs
echo.
echo 📖 See SAVELLA_DEPLOYMENT.md for detailed instructions
echo.
echo 🔑 To generate a SECRET_KEY:
echo    python -c "import secrets; print(secrets.token_urlsafe(32))"
pause
