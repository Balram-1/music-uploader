from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

HTML = """
<h2>🎵 YouTube/Spotify to Google Drive</h2>
<form method="POST">
  <input name="link" placeholder="Enter YouTube/Spotify link" style="width:300px"/>
  <button type="submit">Upload</button>
</form>
<p>{{ message }}</p>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        link = request.form.get("link")
        if link:
            try:
                subprocess.run(["python3", "uploader.py", link], check=True)
                message = "✅ Uploaded Successfully!"
            except Exception as e:
                message = f"❌ Failed: {e}"
    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
