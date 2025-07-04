import os
import subprocess
import sys
import re
from datetime import datetime

# Config
YT_DLP_PATH = "yt-dlp"  # Ensure yt-dlp is in PATH or full path
FFMPEG_PATH = "ffmpeg"  # Ensure ffmpeg is in PATH or full path
RCLONE_REMOTE = "gdrive:music"
TEMP_DIR = "/tmp/music_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

def sanitize_filename(title):
    """Clean filename from unwanted characters."""
    return re.sub(r'[\\/:"*?<>|]+', '', title)[:100].strip()

def download_audio(link):
    """Download highest quality mp3 with thumbnail and metadata."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    outtmpl = os.path.join(TEMP_DIR, f"%(title).100s_%(id)s_{timestamp}.%(ext)s")

    cmd = [
        YT_DLP_PATH,
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",  # best
        "--embed-thumbnail",
        "--add-metadata",
        "--ffmpeg-location", FFMPEG_PATH,
        "-o", outtmpl,
        link
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"[yt-dlp] Error:\n{result.stderr}")

    # Get latest downloaded mp3
    mp3s = [f for f in os.listdir(TEMP_DIR) if f.endswith(".mp3")]
    if not mp3s:
        raise FileNotFoundError("No MP3 file found in output.")

    latest = max(mp3s, key=lambda f: os.path.getctime(os.path.join(TEMP_DIR, f)))
    return os.path.join(TEMP_DIR, latest)

def upload_to_drive(filepath):
    """Upload the mp3 file to Google Drive using rclone."""
    cmd = ["rclone", "copy", filepath, RCLONE_REMOTE]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"[rclone] Upload failed:\n{result.stderr}")
    return os.path.basename(filepath)

def download_and_upload(link):
    """Wrapper function: download -> upload -> return filename."""
    local_path = download_audio(link)
    filename = upload_to_drive(local_path)
    return filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uploader.py <YouTube_or_Spotify_link>")
        sys.exit(1)

    try:
        final_file = download_and_upload(sys.argv[1])
        print(f"[✓] Done! Uploaded as: {final_file}")
    except Exception as e:
        print(f"[✗] Error: {e}")
        sys.exit(1)
