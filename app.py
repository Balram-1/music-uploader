import os
import uuid
import shutil
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Temporary directory for downloads
MUSIC_TEMP_DIR = "/tmp/music_download"
# Your rclone remote and path for Google Drive music folder
GDRIVE_REMOTE = "gdrive:music"

# Ensure temp directory exists
os.makedirs(MUSIC_TEMP_DIR, exist_ok=True)


def run_command(cmd, timeout=600):
    """Run a shell command with timeout, return (exit_code, combined_output)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return 1, str(e)


@app.route('/')
def index():
    """Serve the main frontend page."""
    return render_template('index.html')


@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Create a unique folder for this download job
    job_id = str(uuid.uuid4())
    download_dir = os.path.join(MUSIC_TEMP_DIR, job_id)
    os.makedirs(download_dir, exist_ok=True)

    # Determine which downloader to use
    if "spotify" in url.lower():
        # Use spotdl for Spotify URLs
        cmd = f'spotdl download "{url}" --output "{download_dir}/%(artist)s - %(title)s.%(ext)s"'
    else:
        # Use yt-dlp for YouTube and others, extract audio as mp3 with metadata and thumbnail
        cmd = (
            f'yt-dlp -x --audio-format mp3 '
            f'--embed-thumbnail --embed-metadata '
            f'-o "{download_dir}/%(title)s.%(ext)s" "{url}"'
        )

    # Run the download command
    code, output = run_command(cmd)
    if code != 0:
        shutil.rmtree(download_dir, ignore_errors=True)
        return jsonify({"error": f"Download failed: {output}"}), 500

    # Upload downloaded files to Google Drive using rclone
    code, rclone_output = run_command(f'rclone copy "{download_dir}" "{GDRIVE_REMOTE}" --fast-list')
    if code != 0:
        shutil.rmtree(download_dir, ignore_errors=True)
        return jsonify({"error": f"Upload failed: {rclone_output}"}), 500

    # List uploaded files to return to frontend
    uploaded_files = [f for f in os.listdir(download_dir) if not f.startswith(".")]

    # Clean up temp download directory
    shutil.rmtree(download_dir, ignore_errors=True)

    return jsonify({"file": uploaded_files})


if __name__ == '__main__':
    # Run Flask app on all interfaces, port 5000 (matches your Render config)
    app.run(host='0.0.0.0', port=5000)
