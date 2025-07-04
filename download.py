from flask import Flask, request, jsonify
import subprocess
import os
import re
from datetime import datetime

app = Flask(__name__)

UPLOAD_DIR = "/tmp/music_uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def sanitize_filename(title):
    # Clean and shorten the filename
    title = re.sub(r'[\/:*?"<>|]', '', title)
    return title[:100].strip()

def download_song(link):
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
        return None, result.stderr

    # Find the mp3 file downloaded
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".mp3")]
    if not files:
        return None, "No MP3 downloaded"

    latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_DIR, f)))
    return os.path.join(UPLOAD_DIR, latest_file), None

def upload_to_drive(local_file):
    filename = os.path.basename(local_file)
    drive_path = f"gdrive:/Navidrome/{filename}"
    cmd = ["rclone", "copy", local_file, drive_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stderr
    return True, None

@app.route("/download", methods=["POST"])
def handle_download():
    data = request.json
    link = data.get("link")
    if not link:
        return jsonify({"error": "No link provided"}), 400

    mp3_path, error = download_song(link)
    if error:
        return jsonify({"error": error}), 500

    success, upload_err = upload_to_drive(mp3_path)
    if not success:
        return jsonify({"error": upload_err}), 500

    return jsonify({"message": "Song downloaded and uploaded successfully", "file": os.path.basename(mp3_path)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
