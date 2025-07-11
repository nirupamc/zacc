# 🎵 Spotify/YouTube Playlist Downloader

A full-stack web application that allows users to download Spotify or YouTube playlists/tracks in high-quality audio formats (WAV, FLAC, MP3). Built with Flask backend and vanilla JavaScript frontend.

![App Screenshot](https://via.placeholder.com/800x400?text=Playlist+Downloader+Screenshot)

## ✨ Features

- **Multi-Platform Support**: Download from Spotify, YouTube, and YouTube Music
- **High-Quality Audio**: Choose from MP3, WAV, or FLAC formats
- **No Track Limits**: Handle playlists with hundreds of songs
- **ZIP Archive**: Automatically compresses downloads into a single file
- **Real-time Progress**: Live progress tracking with status updates
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Background Processing**: Non-blocking downloads using threading
- **Auto Cleanup**: Automatically removes old files to save storage

## 🛠️ Tech Stack

- **Backend**: Python Flask, spotDL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Audio Processing**: FFmpeg
- **Deployment**: Docker, Gunicorn

## 📋 Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Internet connection for downloading tracks

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd playlist-downloader
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# On Windows (using Chocolatey):
choco install ffmpeg

# On macOS (using Homebrew):
brew install ffmpeg

# On Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg
```

### 3. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
# At minimum, change the SECRET_KEY for production
```

### 4. ⚠️ **IMPORTANT: Spotify Authentication Setup**

For reliable Spotify downloads, set up API authentication:

1. **Get Spotify Credentials** (5 minutes):

   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Copy Client ID and Client Secret

2. **Add to `.env` file**:

   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

3. **Detailed Setup**: See [`SPOTIFY_SETUP.md`](SPOTIFY_SETUP.md) for complete instructions

**Without authentication**: You may get rate limiting errors with Spotify URLs. YouTube URLs work fine without setup.

### 5. Run the Application

```bash
# Development mode
python app.py

# Production mode with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

### 6. Access the Application

Open your browser and navigate to `http://localhost:5000`

## 🌐 Savella Cloud Deployment

Deploy to Savella cloud hosting for production use:

### Quick Deployment:

```bash
# Run deployment script
./deploy-savella.sh  # Linux/Mac
# or
deploy-savella.bat   # Windows

# Follow the generated instructions
```

### Requirements for Savella:

- Spotify API credentials (required for production)
- Strong SECRET_KEY
- Domain name (optional)

**📖 Complete Guide**: See [`SAVELLA_DEPLOYMENT.md`](SAVELLA_DEPLOYMENT.md) for detailed instructions

## 🚨 Troubleshooting Rate Limiting

If you encounter "rate limit" or "429" errors:

1. **Set up Spotify authentication** (see step 4 above)
2. **Use smaller playlists** (5-10 tracks) for testing
3. **Try YouTube URLs** as an alternative
4. **Wait between downloads** (5-10 minutes for large playlists)
5. **Check [`FIXES_SUMMARY.md`](FIXES_SUMMARY.md)** for detailed solutions

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the image
docker build -t playlist-downloader .

# Run the container
docker run -p 5000:5000 -v $(pwd)/downloads:/app/downloads playlist-downloader
```

### Using Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./downloads:/app/downloads
      - ./output:/app/output
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
```

## 📖 API Documentation

### Start Download

```http
POST /download
Content-Type: application/json

{
  "url": "https://open.spotify.com/playlist/...",
  "format": "wav"
}
```

**Response:**

```json
{
  "task_id": "1641234567_0",
  "status": "started",
  "message": "Download started successfully"
}
```

### Check Status

```http
GET /status/{task_id}
```

**Response:**

```json
{
  "task_id": "1641234567_0",
  "status": "downloading",
  "progress": 45,
  "message": "Downloading tracks...",
  "error": null
}
```

### Download File

```http
GET /download/{task_id}
```

Returns the ZIP file containing all downloaded tracks.

## 🔧 Configuration

### Environment Variables

| Variable            | Default       | Description                             |
| ------------------- | ------------- | --------------------------------------- |
| `FLASK_ENV`         | `development` | Flask environment mode                  |
| `SECRET_KEY`        | Random        | Flask secret key (change in production) |
| `HOST`              | `0.0.0.0`     | Host to bind the server                 |
| `PORT`              | `5000`        | Port to run the server                  |
| `MAX_DOWNLOAD_SIZE` | `1073741824`  | Maximum download size (1GB)             |
| `CLEANUP_INTERVAL`  | `3600`        | Cleanup interval in seconds             |

### Supported Formats

- **MP3**: Compressed format, smaller file size
- **WAV**: Uncompressed format, high quality
- **FLAC**: Lossless compression, best quality

### Supported Platforms

- Spotify (playlists and tracks)
- YouTube (videos and playlists)
- YouTube Music

## 📁 Project Structure

```
playlist-downloader/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── downloads/           # Temporary download directory
├── output/             # ZIP files output directory
├── temp/               # Temporary files
├── templates/
│   └── index.html      # Main HTML template
└── static/
    ├── css/
    │   └── styles.css  # Application styles
    └── js/
        └── app.js      # Frontend JavaScript
```

## 🛡️ Security Considerations

- Change the `SECRET_KEY` in production
- Use HTTPS in production deployment
- Implement rate limiting for public deployments
- Consider user authentication for sensitive deployments
- Regularly update dependencies for security patches

## 📝 Legal Notice

This application is for educational and personal use only. Users are responsible for:

- Respecting copyright laws
- Obtaining proper licenses for downloaded content
- Using downloaded content within legal boundaries
- Complying with terms of service of source platforms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**FFmpeg not found:**

```bash
# Install FFmpeg on your system
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

**Permission denied errors:**

```bash
# Ensure proper permissions for directories
chmod 755 downloads/ output/ temp/
```

**Port already in use:**

```bash
# Change port in .env file or use different port
PORT=8080 python app.py
```

**Large playlist timeout:**

- Increase timeout in Gunicorn configuration
- Consider using background task queue (Celery + Redis)

### Performance Tips

- Use SSD storage for better I/O performance
- Increase worker count for concurrent downloads
- Monitor disk space regularly
- Set up automatic cleanup for old files

## 📞 Support

For support, please:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information
4. Provide logs and error messages

## 🔮 Future Enhancements

- [ ] User authentication and personal libraries
- [ ] Download history and management
- [ ] Batch download from multiple URLs
- [ ] Real-time progress via WebSockets
- [ ] Mobile app (React Native/Flutter)
- [ ] Integration with cloud storage services
- [ ] Advanced audio processing options
- [ ] Playlist organization and tagging

