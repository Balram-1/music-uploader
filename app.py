from flask import Flask, request, jsonify
import os
import subprocess
import uuid
import shutil

app = Flask(__name__)

MUSIC_TEMP_DIR = "/tmp/music_download"
GDRIVE_REMOTE = "gdrive:music"  # Your rclone remote:path

os.makedirs(MUSIC_TEMP_DIR, exist_ok=True)

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Unique subfolder for this download
    job_id = str(uuid.uuid4())
    download_dir = os.path.join(MUSIC_TEMP_DIR, job_id)
    os.makedirs(download_dir, exist_ok=True)

    # Decide which tool to use
    if "spotify" in url.lower():
        # spotdl
        cmd = f"spotdl download \"{url}\" --output \"{download_dir}/%(artist)s - %(title)s.%(ext)s\""
    else:
        # yt-dlp (audio extraction)
        cmd = f"yt-dlp -x --audio-format mp3 --embed-thumbnail --embed-metadata -o \"{download_dir}/%(title)s.%(ext)s\" \"{url}\""

    code, output = run_command(cmd)
    if code != 0:
        shutil.rmtree(download_dir, ignore_errors=True)
        return jsonify({"error": f"Download failed: {output}"}), 500

    # rclone copy to Google Drive
    code, rclone_output = run_command(f"rclone copy \"{download_dir}\" \"{GDRIVE_REMOTE}\" --fast-list")
    if code != 0:
        shutil.rmtree(download_dir, ignore_errors=True)
        return jsonify({"error": f"Upload failed: {rclone_output}"}), 500

    # List uploaded files
    files = [f for f in os.listdir(download_dir) if not f.startswith(".")]
    shutil.rmtree(download_dir, ignore_errors=True)
    return jsonify({"file": files})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
