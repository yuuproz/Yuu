from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import yt_dlp
import tempfile
import os

app = FastAPI(title="Meshook Backend - Universal Downloader + Playlist")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BLOCKED_KEYWORDS = ["netflix.com", "disneyplus.com", "disney+", "primevideo.com", "hulu.com", "hbomax.com", "max.com/watch"]

def is_allowed(url: str):
    low = url.lower()
    for b in BLOCKED_KEYWORDS:
        if b in low:
            return False, f"Blocked DRM platform: {b}"
    return True, "ok"

@app.get("/")
def home():
    return {"name": "Meshook API", "version": "2.0", "features": ["batch", "playlist", "HD selector", "mp3/mp4", "background play"]}

@app.get("/api/info")
def get_info(url: str = Query(...)):
    allowed, msg = is_allowed(url)
    if not allowed:
        raise HTTPException(403, msg)
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": False, # allow playlist detection
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # If playlist, return entries
            if "entries" in info:
                entries = []
                for e in list(info["entries"])[:50]: # limit 50 for free tier
                    if not e: continue
                    entries.append({
                        "id": e.get("id"),
                        "title": e.get("title"),
                        "thumbnail": e.get("thumbnail"),
                        "duration": e.get("duration"),
                        "url": e.get("webpage_url") or e.get("url"),
                    })
                return {
                    "type": "playlist",
                    "title": info.get("title"),
                    "count": len(entries),
                    "entries": entries
                }
            # Single video
            formats = []
            # Build HD selector
            seen_heights = set()
            for f in info.get("formats", []):
                h = f.get("height")
                if h and h not in seen_heights and f.get("vcodec") != "none":
                    seen_heights.add(h)
                    formats.append({
                        "height": h,
                        "ext": f.get("ext"),
                        "filesize": f.get("filesize"),
                        "format_id": f.get("format_id"),
                        "note": f.get("format_note") or f"{h}p",
                        "is_no_watermark": True
                    })
            formats = sorted(formats, key=lambda x: x["height"] or 0, reverse=True)
            return {
                "type": "video",
                "id": info.get("id"),
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "extractor": info.get("extractor"),
                "formats": formats, # HD selector
                "best_url": info.get("url"),
            }
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/api/batch-info")
def batch_info(urls: str = Query(..., description="Comma separated URLs")):
    url_list = [u.strip() for u in urls.split(",") if u.strip()][:10] # max 10 batch
    results = []
    for url in url_list:
        try:
            allowed, msg = is_allowed(url)
            if not allowed:
                results.append({"url": url, "error": msg})
                continue
            ydl_opts = {"quiet": True, "skip_download": True, "noplaylist": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                results.append({
                    "url": url,
                    "title": info.get("title"),
                    "thumbnail": info.get("thumbnail"),
                    "duration": info.get("duration"),
                    "id": info.get("id"),
                })
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return {"count": len(results), "results": results}

@app.get("/api/download")
def download_proxy(url: str = Query(...), format: str = Query("mp4"), quality: str = Query("best", description="720,1080,etc")):
    allowed, msg = is_allowed(url)
    if not allowed:
        raise HTTPException(403, msg)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            if format == "mp3":
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
                    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                    "quiet": True,
                }
            else:
                # HD quality selector
                if quality != "best" and quality.isdigit():
                    fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
                else:
                    fmt = "bestvideo+bestaudio/best"
                ydl_opts = {
                    "format": fmt,
                    "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
                    "merge_output_format": "mp4",
                    "quiet": True,
                }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                files = os.listdir(tmpdir)
                if not files:
                    raise HTTPException(400, "Download failed")
                filepath = os.path.join(tmpdir, files[0])
                filename = f"meshook-{info.get('id','video')}.{format}"
                def iterfile():
                    with open(filepath, "rb") as f:
                        while chunk := f.read(1024*1024):
                            yield chunk
                media = "audio/mpeg" if format=="mp3" else "video/mp4"
                return StreamingResponse(iterfile(), media_type=media, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))
