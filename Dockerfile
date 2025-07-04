FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg curl unzip && \
    # yt-dlp
    pip install yt-dlp spotdl flask && \
    # rclone
    curl -O https://downloads.rclone.org/rclone-current-linux-amd64.deb && \
    dpkg -i rclone-current-linux-amd64.deb && \
    rm rclone-current-linux-amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# Copy rclone config
COPY rclone.conf /root/.config/rclone/rclone.conf

# Copy app code
COPY app.py /app/app.py
WORKDIR /app

EXPOSE 5000

CMD ["python", "app.py"]
