#!/bin/bash
# Quick deployment script for Savella

echo "🚀 Preparing Playlist Downloader for Savella deployment..."

# Clean up development files
echo "🧹 Cleaning up development files..."
rm -rf __pycache__ .pytest_cache *.pyc
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Clear download directories
rm -rf downloads/* temp/* output/* logs/*

# Create production archive
echo "📦 Creating deployment archive..."
tar -czf playlist-downloader-savella.tar.gz \
    --exclude='.git' \
    --exclude='*.tar.gz' \
    --exclude='downloads/*' \
    --exclude='temp/*' \
    --exclude='output/*' \
    --exclude='logs/*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    .

echo "✅ Deployment archive created: playlist-downloader-savella.tar.gz"
echo ""
echo "📋 Next steps for Savella deployment:"
echo "1. Upload playlist-downloader-savella.tar.gz to Savella"
echo "2. Set environment variables:"
echo "   - SECRET_KEY (generate a strong one)"
echo "   - SPOTIFY_CLIENT_ID"
echo "   - SPOTIFY_CLIENT_SECRET"
echo "3. Configure domain and SSL"
echo "4. Monitor the deployment logs"
echo ""
echo "📖 See SAVELLA_DEPLOYMENT.md for detailed instructions"
echo ""
echo "🔑 To generate a SECRET_KEY:"
echo "   python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
