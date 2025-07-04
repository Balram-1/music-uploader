from flask import Flask, request, jsonify, render_template
from download import download_and_upload
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/music_uploads'

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="⚠️ Please enter a YouTube or Spotify link.")
        try:
            filename, error = download_and_upload(url)
            if error:
                return render_template("index.html", error=f"❌ {error}")
            return render_template("index.html", success=f"✅ Downloaded and saved as {filename}")
        except Exception as e:
            return render_template("index.html", error=f"❌ Exception: {str(e)}")
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        data = request.get_json(force=True)
        url = data.get("link") or data.get("url")
        if not url:
            return jsonify({"error": "No URL provided"}), 400

        filename, error = download_and_upload(url)
        if error:
            return jsonify({"error": error}), 500
        return jsonify({"success": True, "file": filename})

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
