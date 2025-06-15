#!/bin/bash

# Set up logging
LOG_DIR="/home/leon/Desktop/automated_projects/EasyApplyJobsBot/logs"
LOG_FILE="$LOG_DIR/bot_$(date +\%Y\%m\%d_\%H\%M\%S).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function for logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Set display for Chrome
export DISPLAY=:10.0

# Set the working directory to the project root
cd /home/leon/Desktop/automated_projects/EasyApplyJobsBot

log "Starting bot run sequence"

# Kill any existing Chrome processes
log "Killing existing Chrome processes"
/home/leon/Desktop/automated_projects/EasyApplyJobsBot/scripts/linux/kill_chrome.sh

# Wait a moment for Chrome to fully close
log "Waiting for Chrome to close"
sleep 2

# Start Chrome in the background
log "Starting Chrome"
/home/leon/Desktop/automated_projects/EasyApplyJobsBot/scripts/linux/start_chrome.sh &

# Wait for Chrome to initialize
log "Waiting for Chrome to initialize"
sleep 2

# Run the bot
log "Starting bot"
/home/leon/.local/bin/uv run main.py --skip-login --verbose --retry-failed 2>&1 | tee -a "$LOG_FILE"

# # Kill Chrome after bot finishes
# log "Killing Chrome after bot completion"
# /home/leon/Desktop/automated_projects/EasyApplyJobsBot/scripts/linux/kill_chrome.sh

log "Bot run sequence completed"

tail -f logs/bot_run_*.log 