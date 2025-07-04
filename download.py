import subprocess
import os
import re
from datetime import datetime

UPLOAD_DIR = "/tmp/music_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(title):
    title = re.sub(r'[\\/:*?"<>|]', '', title)
    return title[:100].strip()

def download_song(link):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_template = os.path.join(UPLOAD_DIR, f"%(title).100s_{timestamp}.%(ext)s")

    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--embed-thumbnail",
        "--add-metadata",
        "--ffmpeg-location", "ffmpeg",
        "--no-playlist",  # Remove this if you want full playlist support
        "-o", output_template,
        link
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return None, f"Download failed: {result.stderr.strip()}"

    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".mp3")]
    if not files:
        return None, "No MP3 file found after download."

    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_DIR, f)))
    return os.path.join(UPLOAD_DIR, latest_file), None

def upload_to_drive(local_file):
    filename = os.path.basename(local_file)
    remote_path = f"gdrive:/Navidrome/{filename}"
    command = ["rclone", "copy", local_file, remote_path]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return False, f"Upload failed: {result.stderr.strip()}"
    return True, None

def download_and_upload(link):
    mp3_path, error = download_song(link)
    if error:
        return None, error

    success, upload_error = upload_to_drive(mp3_path)
    if not success:
        return None, upload_error

    return os.path.basename(mp3_path), None
