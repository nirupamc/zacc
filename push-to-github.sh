#!/bin/bash

echo "================================================"
echo "    Pushing Playlist Downloader to GitHub"
echo "================================================"

echo
echo "Checking git status..."
git status

echo
echo "Adding all files to git..."
git add .

echo
echo "Committing changes..."
read -p "Enter commit message (or press Enter for default): " commit_message
if [ -z "$commit_message" ]; then
    commit_message="Deploy playlist downloader to production"
fi

git commit -m "$commit_message"

echo
echo "Pushing to GitHub..."
git push origin main

echo
echo "================================================"
echo "    Push completed successfully!"
echo "================================================"
echo
echo "Next steps:"
echo "1. Go to your Savella dashboard"
echo "2. Connect your GitHub repository"
echo "3. Set environment variables:"
echo "   - SPOTIFY_CLIENT_ID"
echo "   - SPOTIFY_CLIENT_SECRET"
echo "4. Deploy the application"
echo
echo "Your app will be available at your Savella domain!"
echo "================================================"
