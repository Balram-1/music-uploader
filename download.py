import subprocess
import os
import re
from datetime import datetime

# Directory to temporarily save downloaded songs
UPLOAD_DIR = "/tmp/music_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(title):
    """Remove problematic characters and limit filename length."""
    title = re.sub(r'[\/:*?"<>|]', '', title)
    return title[:100].strip()

def download_song(link):
    """Download a song from YouTube/Spotify using yt-dlp and return the file path."""
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    output_template = os.path.join(UPLOAD_DIR, f"%(title).100s_%(id)s_{now}.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--embed-thumbnail",
        "--add-metadata",
        "-o", output_template,
        link
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, f"Download error:\n{result.stderr}"

    # Find the newest mp3 file in the upload dir
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".mp3")]
    if not files:
        return None, "No MP3 file found after download"

    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_DIR, f)))
    return os.path.join(UPLOAD_DIR, latest_file), None

def upload_to_drive(local_file):
    """Upload the given MP3 file to Google Drive using rclone."""
    filename = os.path.basename(local_file)
    drive_path = f"gdrive:/Navidrome/{filename}"

    cmd = ["rclone", "copy", local_file, drive_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, f"Upload error:\n{result.stderr}"

    return True, None

def download_and_upload(link):
    """Combined function to download a song and upload to drive."""
    mp3_path, error = download_song(link)
    if error:
        return None, error

    success, upload_error = upload_to_drive(mp3_path)
    if not success:
        return None, upload_error

    return os.path.basename(mp3_path), None
