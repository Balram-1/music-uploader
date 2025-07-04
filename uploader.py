import os
import re
import sys
import subprocess
from datetime import datetime

# Configurations
YT_DLP_PATH = "yt-dlp"  # Assumes yt-dlp is in PATH
FFMPEG_PATH = "ffmpeg"  # Assumes ffmpeg is in PATH
UPLOAD_DIR = "/tmp/music_uploads"
RCLONE_REMOTE = "gdrive:/Navidrome"

# Create upload directory if not exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(name):
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    return name.strip()[:100]

def is_spotify_link(link):
    return "open.spotify.com" in link

def download_song(link):
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    output_template = os.path.join(UPLOAD_DIR, f"%(title).100s_%(id)s_{now}.%(ext)s")

    cmd = [
        YT_DLP_PATH,
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",  # Best quality
        "--embed-thumbnail",
        "--add-metadata",
        "--ffmpeg-location", FFMPEG_PATH,
        "-o", output_template,
        link
    ]

    print("[+] Downloading...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, f"Download failed:\n{result.stderr}"

    # Locate the most recent MP3 file
    mp3_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".mp3")]
    if not mp3_files:
        return None, "No MP3 file found after download."

    latest_file = max(mp3_files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_DIR, f)))
    return os.path.join(UPLOAD_DIR, latest_file), None

def upload_to_drive(file_path):
    cmd = ["rclone", "copy", file_path, RCLONE_REMOTE]
    print("[+] Uploading to Google Drive...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, f"Upload failed:\n{result.stderr}"
    return True, None

def convert_spotify_to_youtube(spotify_link):
    # Use yt-dlp's internal support for Spotify (via YouTube search)
    return spotify_link

def download_and_upload(link):
    if is_spotify_link(link):
        print("[i] Spotify link detected. Will attempt best matching download.")
        link = convert_spotify_to_youtube(link)

    file_path, error = download_song(link)
    if error:
        print("[x]", error)
        return

    success, upload_error = upload_to_drive(file_path)
    if not success:
        print("[x]", upload_error)
    else:
        print(f"[✓] Uploaded: {os.path.basename(file_path)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uploader.py <youtube_or_spotify_link>")
        sys.exit(1)

    download_and_upload(sys.argv[1])
