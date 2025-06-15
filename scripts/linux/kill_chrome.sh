#!/bin/bash

# Kill Chrome processes with chrome/chrome in path
pkill -f "chrome/chrome" || true

# Remove Chrome SingletonLock file
rm -f "$HOME/.config/chrome-debug/SingletonLock"

# Additional cleanup for Chrome processes with chrome/chrome in path
ps aux | grep -i "chrome/chrome" | grep -v grep | awk '{print $2}' | xargs -r kill -9 || true

echo "Chrome processes terminated and debug directory cleaned." 