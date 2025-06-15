#!/bin/bash

# Create debug profile directory if it doesn't exist
DEBUG_DIR="$HOME/.config/chrome-debug"
mkdir -p "$DEBUG_DIR"

# Start Chrome with debugging enabled
google-chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="$DEBUG_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --enable-unsafe-swiftshader \
    --disable-gpu-driver-bug-workarounds \
    --disable-gpu-driver-workarounds \
    --disable-gpu-sandbox \
    --disable-software-rasterizer \
    --disable-gpu