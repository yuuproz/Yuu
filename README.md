# Meshook Backend - Free Legal Video Downloader API

This backend powers meshook.vercel.app - downloads ONLY from public legal sources.

## Features
- /api/info?url=LINK -> returns title, thumbnail, best no-watermark URL, formats
- /api/download?url=LINK&format=mp4 or mp3 -> streams file, converts mp3 via ffmpeg
- CORS enabled for your Vercel frontend
- Blocks DRM: Netflix, Disney+, Prime Video, Hulu, Spotify etc
- No storage - streams directly (free tier friendly)

## Supported (via yt-dlp 1000+ sites)
TikTok (no watermark original), Instagram public, YouTube public, Facebook public, Twitter/X, Vimeo, Reddit, Pinterest, Twitch clips, Dailymotion etc.

## Deploy FREE 0 cost
Option 1: Render.com (recommended, has ffmpeg free)
1. Push this folder to GitHub
2. Go to render.com -> New Web Service -> Connect repo
3. Runtime: Docker
4. It will use Dockerfile (includes ffmpeg)
5. After deploy, you get https://meshook-backend.onrender.com

Option 2: HuggingFace Spaces
- Create Space -> Docker -> push

## Connect to your frontend
In your meshook_clone.html, change fetch URL:

fetch(`https://YOUR-BACKEND.onrender.com/api/info?url=${encodeURIComponent(link)}`)

Then for download buttons:
window.location = `https://YOUR-BACKEND.onrender.com/api/download?url=${encodeURIComponent(link)}&format=mp4`

For MP3:
...&format=mp3

## Legal
This backend does NOT bypass DRM. It only fetches what the platform API publicly provides. TikTok "no watermark" is the original file before overlay, not a hack. Users must only download their own content or public domain / with permission. Add Terms on frontend.

## Local run
pip install -r requirements.txt
uvicorn main:app --reload
