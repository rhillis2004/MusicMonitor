FROM python:3.11-slim

# Install beets and watchdog
RUN pip install beets watchdog

# Create app directory
WORKDIR /app

# Copy the monitoring script and config
COPY music_monitor.py /app/
COPY config.yaml /app/


# Set environment variable so beets uses the provided config.yaml
ENV BEETS_CONFIG=/app/config.yaml

# Set the default command
CMD ["python", "music_monitor.py"]
