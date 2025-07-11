# 🔐 Spotify Authentication Setup Guide

To avoid rate limiting issues when downloading from Spotify, you need to set up Spotify API credentials. This is **highly recommended** for reliable downloads.

## 📋 Quick Setup (5 minutes)

### 1. Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **"Create App"**
3. Fill in the details:
   - **App name**: `Playlist Downloader` (or any name you prefer)
   - **App description**: `Personal playlist downloader application`
   - **Website**: `http://localhost:5000` (for local development)
   - **Redirect URI**: `http://localhost:5000/callback` (required but not used)
4. Check the **"I understand and agree"** box
5. Click **"Save"**

### 2. Get Your Credentials

1. Click on your newly created app
2. Click **"Settings"** in the top right
3. You'll see:
   - **Client ID**: Copy this value
   - **Client Secret**: Click "View client secret" and copy this value

### 3. Add Credentials to Your App

1. Open the `.env` file in your project directory
2. Replace the empty values:

```env
# Spotify API Authentication
SPOTIFY_CLIENT_ID=your_actual_client_id_here
SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
```

3. Save the file and restart your application

## ✅ Verification

After adding credentials, you should see this message when starting the app:

```
✅ Spotify authentication configured
```

## 🚫 Without Authentication

If you don't set up authentication, you may encounter:

- Rate limiting errors (HTTP 429)
- "Too many requests" messages
- Failed downloads for Spotify URLs
- Slower download speeds

## 🔒 Security Notes

- Keep your Client Secret private
- Don't commit credentials to version control
- The credentials are only used for metadata lookup, not for account access
- No personal Spotify data is accessed or stored

## 🆘 Troubleshooting

**"Invalid client" errors:**

- Double-check your Client ID and Client Secret
- Make sure there are no extra spaces in your .env file

**Still getting rate limited:**

- Restart the application after adding credentials
- Try downloading smaller playlists first
- Use YouTube URLs as an alternative

## 🎵 Alternative: YouTube-Only Mode

If you prefer not to set up Spotify authentication, you can:

1. Use YouTube playlist URLs directly
2. Convert Spotify playlist URLs to YouTube using online tools
3. Download individual tracks by searching on YouTube

The app will work without Spotify auth, but may be less reliable for Spotify URLs.
