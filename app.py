import os
import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML template with a simple form and message display
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>LoopDev Music Uploader</title>
    <style>
        body { background: #0d0d0d; color: #00ff99; font-family: Arial, sans-serif; padding: 2rem; }
        input[type=text] { width: 80%; padding: 0.5rem; margin-bottom: 1rem; border-radius: 5px; border: none; }
        button { padding: 0.5rem 1rem; background: #00ff99; border: none; border-radius: 5px; cursor: pointer; }
        .message { margin-top: 1rem; font-weight: bold; }
    </style>
</head>
<body>
    <h1>LoopDev Music Uploader</h1>
    <form method="POST">
        <input type="text" name="link" placeholder="Paste YouTube link here" required />
        <button type="submit">Download & Upload</button>
    </form>
    <div class="message">{{ message }}</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        link = request.form.get("link")
        if link:
            try:
                # Run your existing uploader script with the link as argument
                # Assumes uploader.py is in the same directory and executable
                subprocess.run(["python3", "uploader.py", link], check=True)
                message = "✅ Uploaded Successfully!"
            except subprocess.CalledProcessError as e:
                message = f"❌ Download or upload failed: {e}"
            except Exception as e:
                message = f"❌ Unexpected error: {e}"
        else:
            message = "⚠️ Please enter a valid link."
    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    # Run on all interfaces, port 10000 (adjust as needed)
    app.run(host="0.0.0.0", port=10000)
