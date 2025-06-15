# Use Python 3.11 as base image
FROM python:3.11-slim

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    git \
    procps \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy only the necessary files first
COPY requirements.yaml .
COPY src/ src/
COPY main.py .
COPY .env.example .env
COPY scripts/linux/kill_chrome.sh /usr/local/bin/kill_chrome.sh
COPY scripts/linux/start_chrome.sh /usr/local/bin/start_chrome.sh

# Make scripts executable
RUN chmod +x /usr/local/bin/kill_chrome.sh /usr/local/bin/start_chrome.sh

# Create data directory
RUN mkdir -p data

# Install requirements using UV
RUN uv venv
RUN uv pip install -r requirements.yaml

# Create volume for persistent data
VOLUME ["/app/data"]

# Create startup script
RUN echo '#!/bin/bash\n\
# Kill any existing Chrome processes\n\
kill_chrome.sh\n\
\n\
# Start Chrome in the background\n\
start_chrome.sh &\n\
CHROME_PID=$!\n\
\n\
# Wait for Chrome to start\n\
sleep 5\n\
\n\
# Run the bot\n\
uv run main.py --verbose --retry-failed\n\
\n\
# Kill Chrome after bot finishes\n\
kill_chrome.sh\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the bot
CMD ["/app/start.sh"]


