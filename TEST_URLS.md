# 🧪 Test URLs for the Playlist Downloader

Use these URLs to test the application functionality:

## ✅ Working YouTube URLs

### Individual Songs

- **Pop Song**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Rock Song**: `https://www.youtube.com/watch?v=3JZ4pnNtyxQ`

### Small Playlists (Good for testing)

- **Short Music Playlist**: `https://www.youtube.com/playlist?list=PLw-VjHDlEOgs658kAHR_LAaILBXb-s6Q5`
- **Top Hits**: `https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI`

### YouTube Music

- **Liked Songs**: `https://music.youtube.com/playlist?list=LM`
- **Trending**: `https://music.youtube.com/playlist?list=RDCLAK5uy_lf8okgl2ygD075nhnJVjlfhwp`

## ⚠️ Spotify URLs (May cause rate limiting without auth)

### Individual Tracks

- **Popular Song**: `https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh`
- **Classic Rock**: `https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH`

### Small Playlists (Test carefully)

- **Short Playlist**: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- **Today's Top Hits**: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`

## 🔧 Testing Strategy

1. **Start with YouTube URLs** - These work without authentication
2. **Try small playlists first** - 5-10 songs to test functionality
3. **Test different formats** - MP3, WAV, FLAC
4. **Set up Spotify auth** - Follow `SPOTIFY_SETUP.md` for Spotify URLs

## 🚨 Expected Behavior

### Without Spotify Authentication:

- ✅ YouTube URLs should work fine
- ⚠️ Spotify URLs may show rate limiting errors
- 💡 App will suggest setting up authentication

### With Spotify Authentication:

- ✅ Both Spotify and YouTube URLs should work
- 🚀 Better reliability and speed
- 📊 Access to Spotify metadata

## 🐛 Error Testing

To test error handling, try these:

- **Invalid URL**: `https://invalid-url.com/playlist`
- **Private Playlist**: A private Spotify playlist
- **Non-existent ID**: `https://open.spotify.com/playlist/nonexistent123`

## 📝 Notes

- Use smaller playlists for initial testing
- YouTube Music URLs generally work better than regular YouTube
- Individual tracks download faster than playlists
- WAV/FLAC files are much larger than MP3
