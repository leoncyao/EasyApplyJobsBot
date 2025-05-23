# Use Python 3.11 as base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Clone the repository
RUN git clone https://github.com/leoncyao/EasyApplyJobsBot /app

# Set working directory
WORKDIR /app

RUN uv venv

# Install requirements using UV
RUN uv pip install -r requirements.yaml

# Create a script to run the bot
RUN echo '#!/bin/bash\npython3 linkedin.py' > /app/run_bot.sh && \
    chmod +x /app/run_bot.sh

# Set up cron job to run at 12 AM daily
RUN echo "0 0 * * * /app/run_bot.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/easy-apply-cron && \
    chmod 0644 /etc/cron.d/easy-apply-cron

# Create log file
RUN touch /var/log/cron.log

# Start cron in foreground
CMD cron && tail -f /var/log/cron.log 