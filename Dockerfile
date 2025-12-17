
FROM python:3.11-slim


# Set workdir and copy all app files at once for better layer caching
WORKDIR /app
COPY music_monitor.py config.yaml beets_maintenance.sh ./
RUN chmod +x /app/beets_maintenance.sh

# Install beets, watchdog, ffmpeg, cron, and plugin dependencies
RUN apt-get update && apt-get install -y ffmpeg cron \
    && pip install --no-cache-dir beets watchdog requests acoustid langdetect pylast \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Set environment variable so beets uses the provided config.yaml
ENV BEETS_CONFIG=/app/config.yaml


# Add crontab entry for weekly maintenance (every Sunday at 2:00 AM)
RUN echo "0 2 * * 0 /app/beets_maintenance.sh >> /app/beets_maintenance.log 2>&1" > /etc/cron.d/beets-maintenance
RUN crontab /etc/cron.d/beets-maintenance

# Start cron and the main service
CMD bash -c "service cron start && python -u music_monitor.py"
