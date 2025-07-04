import os
import sys
import subprocess

# Paths to executables (use just the command if they're in PATH)
yt_dlp_path = "yt-dlp"      # Use "yt-dlp.exe" if on Windows
ffmpeg_path = "ffmpeg"      # Use "ffmpeg.exe" if on Windows
output_dir = "music"

def download_and_upload(link):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[+] Downloading from: {link}")

    # yt-dlp command to extract audio, convert to mp3, embed thumbnail and metadata
    command = [
        yt_dlp_path,
        "-x", "--audio-format", "mp3",
        "--embed-thumbnail", "--add-metadata",
        "--ffmpeg-location", ffmpeg_path,
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        link
    ]

    try:
        subprocess.run(command, check=True)
        print("[+] Uploading to Google Drive...")
        subprocess.run(["rclone", "copy", output_dir, "gdrive:music"], check=True)
        print("[✓] Done!")
    except subprocess.CalledProcessError as e:
        print(f"[!] Error during download or upload: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uploader.py <YouTube-Link>")
        sys.exit(1)
    download_and_upload(sys.argv[1])
