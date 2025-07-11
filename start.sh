#!/bin/bash
# Production startup script for Savella

echo "🚀 Starting Playlist Downloader for production..."

# Update package list
apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get install -y ffmpeg curl

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements-production.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads temp output logs

# Set proper permissions
chmod 755 downloads temp output logs

# Generate secret key if not provided
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE-THIS-TO-A-STRONG-SECRET-KEY-FOR-PRODUCTION" ]; then
    echo "⚠️  WARNING: Generating random SECRET_KEY. Set a proper one in production!"
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
fi

# Check for Spotify credentials
if [ -z "$SPOTIFY_CLIENT_ID" ] || [ -z "$SPOTIFY_CLIENT_SECRET" ]; then
    echo "⚠️  WARNING: Spotify credentials not configured. This may cause rate limiting."
    echo "   Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
fi

# Start the application with Gunicorn
echo "🌟 Starting application..."
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers ${WORKERS:-2} \
    --timeout ${WORKER_TIMEOUT:-300} \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
