# 🎵 Spotify/YouTube Playlist Downloader - GitHub Deployment Guide

A complete web application for downloading Spotify and YouTube playlists with support for multiple audio formats and ZIP compression.

## 🚀 Quick GitHub + Savella Deployment

### Step 1: Push to GitHub
```bash
# Run the automated script
./push-to-github.bat    # Windows
./push-to-github.sh     # Linux/Mac
```

### Step 2: Setup Savella Hosting
1. **Create Savella Account** at [savella.com](https://savella.com)
2. **Connect GitHub Repository**
   - Go to your Savella dashboard
   - Click "New Project"
   - Select "Import from GitHub"
   - Choose your playlist-downloader repository

3. **Configure Environment Variables**
   In Savella dashboard → Settings → Environment Variables:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   FLASK_ENV=production
   FLASK_DEBUG=false
   ```

4. **Deploy Application**
   - Savella will automatically use `savella.yml` configuration
   - Build will install Python dependencies and FFmpeg
   - App will be available at your Savella domain

### Step 3: Get Spotify API Keys
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Copy Client ID and Client Secret
4. Add these to Savella environment variables

## 📁 Complete File Structure
```
playlist-downloader/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── savella.yml           # Savella configuration
├── .gitignore            # Git ignore rules
├── README.md             # Documentation
├── templates/
│   └── index.html        # Frontend UI
├── static/
│   ├── css/styles.css    # Minimal styling
│   └── js/app.js         # Frontend logic
├── .env.example          # Environment template
└── push-to-github.bat    # Deployment script
```

## ✨ Features
- 🎵 Download Spotify and YouTube playlists
- 🎼 Multiple formats: MP3, WAV, FLAC
- 📦 Automatic ZIP compression
- 🚀 No track limit
- 🎨 Minimal, professional UI
- 🔒 Secure environment variables
- 📱 Responsive design

## 🛠️ Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/playlist-downloader.git
cd playlist-downloader

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Spotify credentials

# Run application
python app.py
```

## 🌐 Production Deployment
The application is configured for production deployment with:
- Gunicorn WSGI server
- Production-grade error handling
- Rate limiting protection
- Health check endpoints
- Automatic retries for API failures

## 📋 Deployment Checklist
- [x] All application files created
- [x] GitHub repository configured
- [x] Savella configuration file (`savella.yml`)
- [x] Environment variables documented
- [x] Deployment scripts ready
- [x] Dependencies listed (`requirements.txt`)
- [x] Error handling implemented
- [x] Health checks configured

## 🔧 Troubleshooting
- **Spotify API errors**: Ensure valid credentials in environment variables
- **Download failures**: Check internet connection and FFmpeg installation
- **Build failures**: Verify Python 3.11 compatibility in requirements

## 📞 Support
For deployment issues, check:
1. Savella build logs
2. Environment variable configuration
3. GitHub repository access
4. Spotify API credentials

Your playlist downloader will be live at: `https://your-app-name.savella.app`
