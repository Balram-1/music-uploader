from flask import Flask, request, jsonify, render_template
from download import download_and_upload

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="Please enter a YouTube or Spotify link.")

        try:
            filename = download_and_upload(url)
            return render_template("index.html", success=f"Downloaded and saved as {filename}")
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        filename = download_and_upload(url)
        return jsonify({"success": True, "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
