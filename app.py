"""
Spotify/YouTube Playlist Downloader Web App
Backend Flask Application with spotDL integration
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import threading
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import zipfile
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse, parse_qs
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Production security settings
if os.getenv('FLASK_ENV') == 'production':
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
    )
    
    # Rate limiting for production
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://"
        )
        logger.info("Rate limiting enabled for production")
    except ImportError:
        app.logger.warning("flask-limiter not installed, rate limiting disabled")
        limiter = None
else:
    limiter = None

# Track app start time for metrics
app.start_time = time.time()

# Add security headers for production
@app.after_request
def add_security_headers(response):
    if os.getenv('FLASK_ENV') == 'production':
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DOWNLOADS_DIR = Path('downloads')
TEMP_DIR = Path('temp')
OUTPUT_DIR = Path('output')

# Create directories if they don't exist
for directory in [DOWNLOADS_DIR, TEMP_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True)

# Thread pool for handling downloads
executor = ThreadPoolExecutor(max_workers=3)

# Store download tasks
download_tasks = {}

# Rate limiting for Spotify API
last_request_time = 0
min_request_interval = 1.0  # 1 second between requests

class DownloadTask:
    """Class to track download progress and status"""
    def __init__(self, task_id, url, format_type):
        self.task_id = task_id
        self.url = url
        self.format_type = format_type
        self.status = 'pending'  # pending, downloading, processing, completed, error
        self.progress = 0
        self.message = 'Initializing download...'
        self.error = None
        self.output_file = None
        self.created_at = datetime.now()

def validate_url(url):
    """Validate if the URL is from supported platforms"""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip().lower()
    supported_domains = [
        'spotify.com',
        'open.spotify.com',
        'youtube.com',
        'youtu.be',
        'music.youtube.com'
    ]
    
    # Check if it's a valid URL format
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
    except Exception:
        return False
    
    return any(domain in url for domain in supported_domains) and url.startswith('http')

def is_spotify_url(url):
    """Check if URL is from Spotify"""
    return 'spotify.com' in url.lower()

def is_youtube_url(url):
    """Check if URL is from YouTube"""
    url_lower = url.lower()
    return any(domain in url_lower for domain in ['youtube.com', 'youtu.be', 'music.youtube.com'])

def exponential_backoff(attempt, base_delay=1, max_delay=60):
    """Calculate exponential backoff delay"""
    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
    return min(delay, max_delay)

def rate_limit():
    """Implement rate limiting for API calls"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < min_request_interval:
        sleep_time = min_request_interval - time_since_last
        time.sleep(sleep_time)
    
    last_request_time = time.time()

def validate_format(format_type):
    """Validate if the format is supported"""
    return format_type in ['wav', 'flac', 'mp3']

def clean_old_files():
    """Clean up old downloads and temporary files"""
    try:
        current_time = time.time()
        cleanup_age = 3600  # 1 hour in seconds
        
        for directory in [DOWNLOADS_DIR, TEMP_DIR, OUTPUT_DIR]:
            if directory.exists():
                for file_path in directory.glob('*'):
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > cleanup_age:
                            file_path.unlink()
                            app.logger.info(f"Cleaned up old file: {file_path}")
                    elif file_path.is_dir():
                        dir_age = current_time - file_path.stat().st_mtime
                        if dir_age > cleanup_age:
                            shutil.rmtree(file_path)
                            app.logger.info(f"Cleaned up old directory: {file_path}")
    except Exception as e:
        app.logger.error(f"Error during cleanup: {e}")

def download_playlist(task_id, url, format_type):
    """Download playlist using spotDL with enhanced error handling and retry logic"""
    task = download_tasks[task_id]
    max_retries = 3
    base_delay = 5
    
    try:
        # Update task status
        task.status = 'downloading'
        task.message = 'Initializing download...'
        logger.info(f"Starting download for task {task_id}, URL: {url}, Format: {format_type}")
        
        # Create unique directory for this download
        download_dir = DOWNLOADS_DIR / f"download_{task_id}"
        download_dir.mkdir(exist_ok=True)
        
        # Implement rate limiting
        rate_limit()
        
        # Try different approaches based on URL type
        success = False
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = exponential_backoff(attempt, base_delay)
                    logger.info(f"Retrying download (attempt {attempt + 1}/{max_retries}) after {delay:.2f}s delay")
                    task.message = f'Retrying download (attempt {attempt + 1}/{max_retries})...'
                    time.sleep(delay)
                
                # Update progress
                task.message = f'Downloading tracks... (attempt {attempt + 1}/{max_retries})'
                task.progress = 25
                
                # Prepare spotDL command with enhanced options
                cmd = [
                    sys.executable, '-m', 'spotdl',
                    url,
                    '--format', format_type,
                    '--output', str(download_dir),
                    '--threads', '2',  # Reduced threads to avoid rate limiting
                    '--bitrate', '320k',
                    '--max-retries', '5',
                    '--sponsor-block',  # Skip sponsor segments in YouTube
                ]
                
                # Add specific options based on URL type
                if is_spotify_url(url):
                    # For Spotify URLs, use specific audio providers and retry settings
                    cmd.extend([
                        '--audio', 'youtube', 'youtube-music',
                        '--lyrics', 'genius', 'musixmatch',
                        '--dont-filter-results',  # Reduce API calls
                    ])
                    
                    # Add Spotify authentication if available
                    client_id = os.getenv('SPOTIFY_CLIENT_ID')
                    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
                    if client_id and client_secret:
                        cmd.extend(['--client-id', client_id, '--client-secret', client_secret])
                        logger.info("Using Spotify authentication")
                    else:
                        logger.warning("No Spotify credentials found. This may cause rate limiting.")
                        # Add longer delay for unauthenticated requests
                        time.sleep(2)
                
                elif is_youtube_url(url):
                    cmd.extend([
                        '--audio', 'youtube-music', 'youtube',
                        '--ytm-data',  # Use YouTube Music data when available
                    ])
                
                logger.info(f"Running command: {' '.join(cmd)}")
                
                # Run spotDL with timeout and better error handling
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=1800,  # 30 minutes timeout
                    cwd=str(Path.cwd())
                )
                
                if process.returncode == 0:
                    success = True
                    logger.info(f"Download successful for task {task_id}")
                    break
                else:
                    error_msg = process.stderr.strip()
                    logger.error(f"spotDL failed (attempt {attempt + 1}): {error_msg}")
                    
                    # Check for specific error types
                    if any(keyword in error_msg.lower() for keyword in ['rate limit', '429', 'too many requests']):
                        if attempt < max_retries - 1:
                            delay = exponential_backoff(attempt + 1, base_delay * 2)  # Longer delay for rate limits
                            logger.info(f"Rate limit detected, waiting {delay:.2f}s before retry")
                            task.message = f'Rate limited, waiting {delay:.0f}s before retry...'
                            time.sleep(delay)
                            continue
                    elif any(keyword in error_msg.lower() for keyword in ['404', 'not found', 'invalid']):
                        # Don't retry for 404 errors
                        raise Exception(f"Content not found or URL invalid: {error_msg}")
                    elif any(keyword in error_msg.lower() for keyword in ['network', 'connection', 'timeout']):
                        # Network issues - retry with longer delay
                        if attempt < max_retries - 1:
                            delay = exponential_backoff(attempt + 1, base_delay)
                            logger.info(f"Network error detected, waiting {delay:.2f}s before retry")
                            time.sleep(delay)
                            continue
                    
                    if attempt == max_retries - 1:
                        raise Exception(f"Download failed after {max_retries} attempts: {error_msg}")
            
            except subprocess.TimeoutExpired:
                logger.error(f"Download timeout for task {task_id} (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    raise Exception("Download timed out. The playlist might be too large or there are network issues.")
            except Exception as e:
                logger.error(f"Download error for task {task_id} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
        
        if not success:
            raise Exception("Download failed after all retry attempts")
        
        # Check if any files were downloaded
        downloaded_files = list(download_dir.rglob('*'))
        audio_files = [f for f in downloaded_files if f.is_file() and f.suffix.lower() in ['.mp3', '.wav', '.flac', '.m4a', '.ogg']]
        
        if not audio_files:
            raise Exception("No audio files were downloaded. The playlist might be empty or inaccessible.")
        
        logger.info(f"Downloaded {len(audio_files)} files for task {task_id}")
        
        # Update progress
        task.status = 'processing'
        task.message = f'Creating archive ({len(audio_files)} files)...'
        task.progress = 75
        
        # Create ZIP file
        zip_filename = f"playlist_{task_id}_{format_type}.zip"
        zip_path = OUTPUT_DIR / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in download_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(download_dir)
                    zipf.write(file_path, arcname)
                    logger.debug(f"Added to ZIP: {arcname}")
        
        # Clean up download directory
        shutil.rmtree(download_dir)
        
        # Update task completion
        task.status = 'completed'
        task.message = f'Download completed! {len(audio_files)} tracks downloaded.'
        task.progress = 100
        task.output_file = str(zip_path)
        
        logger.info(f"Download completed successfully: {zip_path}")
        
    except subprocess.TimeoutExpired:
        task.status = 'error'
        task.error = 'Download timed out. The playlist might be too large or there are network issues.'
        task.message = 'Download timed out'
        logger.error(f"Download timeout for task {task_id}")
    except Exception as e:
        error_msg = str(e)
        task.status = 'error'
        task.error = error_msg
        task.message = f'Download failed: {error_msg}'
        logger.error(f"Download error for task {task_id}: {e}")
        
        # Clean up on error
        download_dir = DOWNLOADS_DIR / f"download_{task_id}"
        if download_dir.exists():
            shutil.rmtree(download_dir)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    """Start a new download task"""
    # Apply rate limiting in production
    if limiter and os.getenv('FLASK_ENV') == 'production':
        try:
            limiter.limit("5 per minute")(lambda: None)()
        except Exception as e:
            return jsonify({'error': 'Rate limit exceeded. Please wait before starting another download.'}), 429
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        format_type = data.get('format', 'mp3').lower()
        
        # Validate inputs
        if not validate_url(url):
            return jsonify({'error': 'Invalid or unsupported URL. Please provide a Spotify or YouTube URL.'}), 400
        
        if not validate_format(format_type):
            return jsonify({'error': 'Invalid format. Supported formats: wav, flac, mp3'}), 400
        
        # Check for Spotify URL and warn about rate limiting if no auth
        if is_spotify_url(url):
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            if not client_id or not client_secret:
                logger.warning("Spotify URL detected but no authentication configured. This may cause rate limiting.")
        
        # Generate unique task ID
        task_id = f"{int(time.time())}_{len(download_tasks)}"
        
        # Create download task
        task = DownloadTask(task_id, url, format_type)
        download_tasks[task_id] = task
        
        # Start download in background
        executor.submit(download_playlist, task_id, url, format_type)
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Download started successfully',
            'warning': 'Spotify rate limiting may occur without proper authentication' if is_spotify_url(url) and not os.getenv('SPOTIFY_CLIENT_ID') else None
        })
        
    except Exception as e:
        logger.error(f"Error starting download: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/status/<task_id>')
def get_status(task_id):
    """Get download status for a specific task"""
    task = download_tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify({
        'task_id': task_id,
        'status': task.status,
        'progress': task.progress,
        'message': task.message,
        'error': task.error,
        'created_at': task.created_at.isoformat()
    })

@app.route('/download/<task_id>')
def download_file(task_id):
    """Download the completed file"""
    task = download_tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if task.status != 'completed':
        return jsonify({'error': 'Download not completed yet'}), 400
    
    if not task.output_file or not Path(task.output_file).exists():
        return jsonify({'error': 'Output file not found'}), 404
    
    try:
        return send_file(
            task.output_file,
            as_attachment=True,
            download_name=f'playlist_{task.format_type}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        return jsonify({'error': 'Error sending file'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_tasks': len([t for t in download_tasks.values() if t.status in ['pending', 'downloading', 'processing']])
    })

@app.route('/metrics')
def metrics():
    """Metrics endpoint for monitoring"""
    if os.getenv('FLASK_ENV') != 'production':
        return jsonify({'error': 'Metrics only available in production'}), 404
    
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return jsonify({
            'active_downloads': len([t for t in download_tasks.values() if t.status in ['downloading', 'processing']]),
            'completed_downloads': len([t for t in download_tasks.values() if t.status == 'completed']),
            'failed_downloads': len([t for t in download_tasks.values() if t.status == 'error']),
            'total_tasks': len(download_tasks),
            'uptime_seconds': int(time.time() - app.start_time),
            'memory_usage_mb': memory_info.rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'disk_usage': {
                'downloads': get_directory_size(DOWNLOADS_DIR),
                'output': get_directory_size(OUTPUT_DIR),
                'temp': get_directory_size(TEMP_DIR)
            }
        })
    except ImportError:
        return jsonify({
            'active_downloads': len([t for t in download_tasks.values() if t.status in ['downloading', 'processing']]),
            'completed_downloads': len([t for t in download_tasks.values() if t.status == 'completed']),
            'failed_downloads': len([t for t in download_tasks.values() if t.status == 'error']),
            'uptime_seconds': int(time.time() - app.start_time),
            'note': 'psutil not available, limited metrics'
        })

def get_directory_size(path):
    """Get directory size in MB"""
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return round(total_size / 1024 / 1024, 2)  # MB
    except Exception:
        return 0

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# Clean up old files on startup
clean_old_files()

# Schedule periodic cleanup
def periodic_cleanup():
    while True:
        time.sleep(3600)  # Run every hour
        clean_old_files()

cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    # Check if spotDL is installed
    try:
        subprocess.run([sys.executable, '-m', 'spotdl', '--help'], 
                      capture_output=True, check=True)
        print("✅ spotDL is installed and ready")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ spotDL is not installed. Please install it with: pip install spotdl")
        sys.exit(1)
    
    # Check Spotify authentication
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if client_id and client_secret:
        print("✅ Spotify authentication configured")
    else:
        print("⚠️  Spotify authentication not configured")
        print("   This may cause rate limiting for Spotify URLs")
        print("   See SPOTIFY_SETUP.md for setup instructions")
    
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
