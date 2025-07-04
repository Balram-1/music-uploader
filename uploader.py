import os
import subprocess
import sys

yt_dlp_path = "yt-dlp.exe"
ffmpeg_path = "ffmpeg.exe"
output_dir = "music"

os.makedirs(output_dir, exist_ok=True)

def download_and_upload(link):
    print(f"[+] Downloading from: {link}")
    
    command = [
        yt_dlp_path,
        "-x", "--audio-format", "mp3",
        "--embed-thumbnail", "--add-metadata",
        "--ffmpeg-location", ffmpeg_path,
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        link
    ]

    subprocess.run(command, check=True)

    print("[+] Uploading to Google Drive...")
    subprocess.run(["rclone", "copy", output_dir, "gdrive:music"], check=True)

    print("[✓] Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uploader.py <youtube_or_spotify_link>")
    else:
        download_and_upload(sys.argv[1])
