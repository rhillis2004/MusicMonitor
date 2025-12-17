
FROM python:3.11-slim

# Set workdir and copy all app files at once for better layer caching
WORKDIR /app
COPY music_monitor.py config.yaml ./

# Install beets and watchdog efficiently
RUN pip install --no-cache-dir beets watchdog \
	&& apt-get update && apt-get install -y ffmpeg \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variable so beets uses the provided config.yaml
ENV BEETS_CONFIG=/app/config.yaml

# Use exec form for CMD
CMD ["python", "-u", "music_monitor.py"]
