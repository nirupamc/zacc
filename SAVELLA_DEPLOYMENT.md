# 🚀 Savella Deployment Guide

This guide will help you deploy the Spotify/YouTube Playlist Downloader to Savella cloud hosting.

## 📋 Prerequisites

- Savella account with hosting plan
- Domain name (optional, Savella provides subdomains)
- Spotify API credentials (recommended for reliability)

## 🎯 Deployment Options

### Option 1: Docker Deployment (Recommended)

### Option 2: Direct Python Deployment

### Option 3: Static + Serverless Functions

---

## 🐳 Option 1: Docker Deployment (Recommended)

### 1. Prepare Environment Variables

Create a production `.env` file:

```env
# Production Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
HOST=0.0.0.0
PORT=8080

# Download Configuration
MAX_DOWNLOAD_SIZE=2147483648  # 2GB for cloud
CLEANUP_INTERVAL=1800  # 30 minutes for cloud storage
MAX_CONCURRENT_DOWNLOADS=2

# Logging
LOG_LEVEL=INFO

# Spotify API (REQUIRED for production)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Cloud Storage (if using external storage)
# AWS_ACCESS_KEY_ID=your_aws_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret
# S3_BUCKET_NAME=your_bucket_name
```

### 2. Build and Deploy

```bash
# Build Docker image
docker build -t playlist-downloader .

# Tag for Savella registry
docker tag playlist-downloader your-savella-registry/playlist-downloader:latest

# Push to Savella
docker push your-savella-registry/playlist-downloader:latest
```

### 3. Savella Configuration

Create `savella.yml`:

```yaml
version: "3.8"
services:
  app:
    image: your-registry/playlist-downloader:latest
    ports:
      - "80:8080"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
      - SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET}
    volumes:
      - downloads:/app/downloads
      - output:/app/output
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  downloads:
  output:
```

---

## 🐍 Option 2: Direct Python Deployment

### 1. Requirements for Savella

Create `requirements-production.txt`:

```txt
Flask==3.0.0
spotdl==4.2.5
python-dotenv==1.0.0
gunicorn==21.2.0
Werkzeug==3.0.1
psutil==5.9.6
requests==2.31.0
```

### 2. Production Startup Script

Create `start.sh`:

```bash
#!/bin/bash
# Production startup script for Savella

# Install system dependencies
apt-get update
apt-get install -y ffmpeg curl

# Install Python dependencies
pip install -r requirements-production.txt

# Create necessary directories
mkdir -p downloads temp output

# Set proper permissions
chmod 755 downloads temp output

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 300 --keep-alive 2 app:app
```

### 3. Savella App Configuration

```yaml
# savella-app.yml
name: playlist-downloader
runtime: python3.11
memory: 2GB
disk: 10GB

build:
  commands:
    - pip install -r requirements-production.txt
    - chmod +x start.sh

start:
  command: ./start.sh

env:
  FLASK_ENV: production
  PORT: 8080

secrets:
  - SECRET_KEY
  - SPOTIFY_CLIENT_ID
  - SPOTIFY_CLIENT_SECRET
```

---

## ⚡ Option 3: Serverless Functions (Advanced)

### 1. API Function

Create `api/download.py`:

```python
from flask import Flask, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    # Implement serverless download logic
    return jsonify({"status": "processing", "id": "task_id"})

if __name__ == '__main__':
    app.run()
```

### 2. Serverless Configuration

```yaml
# savella-functions.yml
functions:
  download:
    runtime: python3.11
    handler: api/download.app
    timeout: 300
    memory: 1GB
    environment:
      SPOTIFY_CLIENT_ID: ${SPOTIFY_CLIENT_ID}
      SPOTIFY_CLIENT_SECRET: ${SPOTIFY_CLIENT_SECRET}

static:
  - path: /
    directory: static
  - path: /templates
    directory: templates
```

---

## 🔧 Production Optimizations

### 1. Update Dockerfile for Production

```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Create directories
RUN mkdir -p downloads temp output

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Production settings
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "--preload", "app:app"]
```

### 2. Enhanced Environment Configuration

Update your `.env` for production:

```env
# Production Environment for Savella
FLASK_ENV=production
SECRET_KEY=generate-a-strong-secret-key-here
HOST=0.0.0.0
PORT=8080

# Performance Settings
MAX_DOWNLOAD_SIZE=2147483648  # 2GB
CLEANUP_INTERVAL=1800  # 30 minutes
MAX_CONCURRENT_DOWNLOADS=2
WORKER_TIMEOUT=300

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/app/logs/app.log

# Spotify API (REQUIRED)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Security
TRUSTED_HOSTS=your-domain.savella.com,*.savella.com
CORS_ORIGINS=https://your-domain.savella.com

# Monitoring
ENABLE_METRICS=true
HEALTH_CHECK_PATH=/health
```

---

## 🔒 Security for Production

### 1. Update app.py for Production Security

Add this to your `app.py`:

```python
# Production security settings
if os.getenv('FLASK_ENV') == 'production':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
    )

    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response
```

### 2. Rate Limiting for Production

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/download', methods=['POST'])
@limiter.limit("5 per minute")
def start_download():
    # Your existing download logic
    pass
```

---

## 🚀 Deployment Steps for Savella

### 1. Prepare Your Code

```bash
# Clean up development files
rm -rf __pycache__ *.pyc .pytest_cache
rm -f app.log

# Create production archive
tar -czf playlist-downloader.tar.gz \
    --exclude='.git' \
    --exclude='downloads/*' \
    --exclude='temp/*' \
    --exclude='output/*' \
    .
```

### 2. Deploy to Savella

```bash
# Using Savella CLI
savella login
savella create playlist-downloader
savella deploy playlist-downloader.tar.gz

# Or using web interface
# Upload the tar.gz file through Savella dashboard
```

### 3. Configure Environment Variables

In Savella dashboard:

1. Go to your app settings
2. Add environment variables:
   - `SECRET_KEY` (generate a strong one)
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
3. Set scaling options (2 workers recommended)

### 4. Set Up Domain (Optional)

```bash
# Connect custom domain
savella domain add playlist-downloader yourdomain.com
savella ssl enable playlist-downloader
```

---

## 📊 Monitoring & Maintenance

### 1. Add Monitoring Endpoint

```python
@app.route('/metrics')
def metrics():
    if os.getenv('FLASK_ENV') != 'production':
        return jsonify({'error': 'Not available in development'}), 404

    return jsonify({
        'active_downloads': len([t for t in download_tasks.values() if t.status in ['downloading', 'processing']]),
        'completed_downloads': len([t for t in download_tasks.values() if t.status == 'completed']),
        'failed_downloads': len([t for t in download_tasks.values() if t.status == 'error']),
        'uptime': time.time() - app.start_time,
        'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
    })
```

### 2. Log Management

```python
# Production logging configuration
if os.getenv('FLASK_ENV') == 'production':
    import logging
    from logging.handlers import RotatingFileHandler

    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

---

## ✅ Final Checklist

Before deploying to Savella:

- [ ] Set up Spotify API credentials
- [ ] Generate strong SECRET_KEY for production
- [ ] Test Docker build locally
- [ ] Configure environment variables
- [ ] Set up monitoring and logging
- [ ] Test with small playlists first
- [ ] Configure domain and SSL
- [ ] Set up automated backups
- [ ] Monitor resource usage

## 🆘 Troubleshooting Production Issues

### Common Savella Deployment Issues:

1. **Memory limits**: Reduce `MAX_CONCURRENT_DOWNLOADS`
2. **Timeout errors**: Increase worker timeout settings
3. **Storage issues**: Implement cleanup more frequently
4. **Rate limiting**: Ensure Spotify auth is configured

### Performance Optimization:

1. **Use CDN** for static files
2. **Enable gzip compression**
3. **Implement caching** for repeated requests
4. **Monitor resource usage** regularly

**Your app is now ready for Savella deployment!** 🚀
