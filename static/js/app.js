/**
 * Spotify/YouTube Playlist Downloader
 * Frontend JavaScript Application
 */

class PlaylistDownloader {
    constructor() {
        this.currentTaskId = null;
        this.pollInterval = null;
        this.initializeElements();
        this.bindEvents();
        this.resetForm();
    }

    initializeElements() {
        // Form elements
        this.urlInput = document.getElementById('url-input');
        this.formatSelect = document.getElementById('format-select');
        this.downloadBtn = document.getElementById('download-btn');

        // Progress elements
        this.progressSection = document.getElementById('progress-section');
        this.progressFill = document.getElementById('progress-fill');
        this.progressPercentage = document.getElementById('progress-percentage');
        this.progressMessage = document.getElementById('progress-message');

        // Result elements
        this.resultSection = document.getElementById('result-section');
        this.successResult = document.getElementById('success-result');
        this.errorResult = document.getElementById('error-result');
        this.errorMessage = document.getElementById('error-message');
        this.downloadFileBtn = document.getElementById('download-file-btn');
        this.retryBtn = document.getElementById('retry-btn');
    }

    bindEvents() {
        this.downloadBtn.addEventListener('click', () => this.startDownload());
        this.retryBtn.addEventListener('click', () => this.resetForm());
        this.downloadFileBtn.addEventListener('click', () => this.downloadFile());
        
        // Enter key support for URL input
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.downloadBtn.disabled) {
                this.startDownload();
            }
        });

        // URL validation on input
        this.urlInput.addEventListener('input', () => this.validateUrl());
    }

    validateUrl() {
        const url = this.urlInput.value.trim();
        const isValid = this.isValidUrl(url);
        
        if (url && !isValid) {
            this.urlInput.style.borderColor = 'var(--error-color)';
        } else {
            this.urlInput.style.borderColor = '';
        }
        
        return isValid || !url;
    }

    isValidUrl(url) {
        if (!url || typeof url !== 'string') return false;
        
        const urlLower = url.toLowerCase().trim();
        const supportedDomains = [
            'spotify.com',
            'open.spotify.com',
            'youtube.com',
            'youtu.be',
            'music.youtube.com'
        ];
        
        return urlLower.startsWith('http') && 
               supportedDomains.some(domain => urlLower.includes(domain));
    }

    async startDownload() {
        const url = this.urlInput.value.trim();
        const format = this.formatSelect.value;

        // Validate input
        if (!url) {
            this.showError('Please enter a playlist or track URL');
            this.urlInput.focus();
            return;
        }

        if (!this.isValidUrl(url)) {
            this.showError('Please enter a valid Spotify or YouTube URL');
            this.urlInput.focus();
            return;
        }

        try {
            this.setDownloadState(true);
            this.showProgress();

            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, format })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start download');
            }

            this.currentTaskId = data.task_id;
            this.startProgressPolling();

            // Show warning if Spotify auth not configured
            if (data.warning) {
                this.showNotification(data.warning, 'warning');
            }

        } catch (error) {
            console.error('Download error:', error);
            this.showError(error.message || 'Failed to start download');
            this.setDownloadState(false);
        }
    }

    startProgressPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(async () => {
            try {
                await this.checkProgress();
            } catch (error) {
                console.error('Progress check error:', error);
                this.stopProgressPolling();
                this.showError('Failed to check download progress');
            }
        }, 2000); // Poll every 2 seconds
    }

    stopProgressPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async checkProgress() {
        if (!this.currentTaskId) return;

        const response = await fetch(`/status/${this.currentTaskId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get status');
        }

        this.updateProgress(data.progress, data.message);

        if (data.status === 'completed') {
            this.stopProgressPolling();
            this.showSuccess();
        } else if (data.status === 'error') {
            this.stopProgressPolling();
            this.showError(data.error || 'Download failed');
        }
    }

    updateProgress(progress, message) {
        this.progressFill.style.width = `${progress}%`;
        this.progressPercentage.textContent = `${progress}%`;
        this.progressMessage.textContent = message;
    }

    async downloadFile() {
        if (!this.currentTaskId) {
            this.showError('No download available');
            return;
        }

        try {
            const response = await fetch(`/download/${this.currentTaskId}`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Download failed');
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `playlist_${this.formatSelect.value}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            window.URL.revokeObjectURL(downloadUrl);

            // Show download success message
            this.showNotification('File downloaded successfully!', 'success');

        } catch (error) {
            console.error('File download error:', error);
            this.showError(error.message || 'Failed to download file');
        }
    }

    showProgress() {
        this.hideAllSections();
        this.progressSection.style.display = 'block';
        this.progressSection.classList.add('fade-in');
        this.updateProgress(0, 'Initializing download...');
    }

    showSuccess() {
        this.hideAllSections();
        this.resultSection.style.display = 'block';
        this.successResult.style.display = 'block';
        this.resultSection.classList.add('fade-in');
        this.setDownloadState(false);
    }

    showError(message) {
        this.hideAllSections();
        this.resultSection.style.display = 'block';
        this.errorResult.style.display = 'block';
        
        // Enhanced error message with suggestions
        let enhancedMessage = message;
        if (message.includes('rate limit') || message.includes('429') || message.includes('too many requests')) {
            enhancedMessage = `${message}\n\n💡 Suggestions:\n• Set up Spotify API authentication (see SPOTIFY_SETUP.md)\n• Try a smaller playlist first\n• Use a YouTube playlist URL instead\n• Wait a few minutes before trying again`;
        } else if (message.includes('404') || message.includes('not found')) {
            enhancedMessage = `${message}\n\n💡 Suggestions:\n• Check if the playlist/track is public\n• Verify the URL is correct\n• Try copying the URL again from Spotify/YouTube`;
        } else if (message.includes('network') || message.includes('connection')) {
            enhancedMessage = `${message}\n\n💡 Suggestions:\n• Check your internet connection\n• Try again in a few moments\n• Use a VPN if the service is blocked in your region`;
        }
        
        this.errorMessage.textContent = enhancedMessage;
        this.errorMessage.style.whiteSpace = 'pre-line'; // Allow line breaks
        this.resultSection.classList.add('fade-in');
        this.setDownloadState(false);
        this.stopProgressPolling();
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        let icon = 'fa-info-circle';
        let backgroundColor = 'var(--primary-color)';
        
        if (type === 'success') {
            icon = 'fa-check';
            backgroundColor = 'var(--success-color)';
        } else if (type === 'warning') {
            icon = 'fa-exclamation-triangle';
            backgroundColor = 'var(--warning-color)';
        } else if (type === 'error') {
            icon = 'fa-times';
            backgroundColor = 'var(--error-color)';
        }
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;

        // Add notification styles
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            backgroundColor: backgroundColor,
            color: 'white',
            borderRadius: 'var(--border-radius)',
            boxShadow: 'var(--shadow)',
            zIndex: '1000',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            maxWidth: '350px',
            animation: 'slideInRight 0.3s ease-out'
        });

        document.body.appendChild(notification);

        // Remove notification after delay (longer for warnings)
        const delay = type === 'warning' ? 6000 : 3000;
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, delay);
    }

    hideAllSections() {
        this.progressSection.style.display = 'none';
        this.resultSection.style.display = 'none';
        this.successResult.style.display = 'none';
        this.errorResult.style.display = 'none';
        
        // Remove animation classes
        [this.progressSection, this.resultSection].forEach(el => {
            el.classList.remove('fade-in');
        });
    }

    setDownloadState(isDownloading) {
        this.downloadBtn.disabled = isDownloading;
        this.urlInput.disabled = isDownloading;
        this.formatSelect.disabled = isDownloading;

        if (isDownloading) {
            this.downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            this.downloadBtn.classList.add('loading');
        } else {
            this.downloadBtn.innerHTML = '<i class="fas fa-download"></i> Start Download';
            this.downloadBtn.classList.remove('loading');
        }
    }

    resetForm() {
        this.stopProgressPolling();
        this.hideAllSections();
        this.setDownloadState(false);
        this.currentTaskId = null;
        this.urlInput.focus();
    }

    // Utility method to format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Utility method to format duration
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// Add notification animations to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 Playlist Downloader initialized');
    new PlaylistDownloader();
});

// Handle page visibility changes to pause/resume polling
document.addEventListener('visibilitychange', () => {
    if (window.playlistDownloader) {
        if (document.hidden) {
            // Page is hidden, could pause polling or reduce frequency
            console.log('Page hidden - continuing polling');
        } else {
            // Page is visible again
            console.log('Page visible - resuming normal polling');
        }
    }
});

// Handle before unload to warn about ongoing downloads
window.addEventListener('beforeunload', (e) => {
    if (window.playlistDownloader && window.playlistDownloader.currentTaskId) {
        const message = 'A download is in progress. Are you sure you want to leave?';
        e.returnValue = message;
        return message;
    }
});

// Export for potential debugging
window.PlaylistDownloader = PlaylistDownloader;
