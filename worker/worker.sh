#!/usr/bin/env bash

remoteDebugPort=9222
chromeBinary="chromium-browser"

chromeVersion=$("$chromeBinary" --version | grep -oE "\d{1,4}" | head -n1)

"$chromeBinary" --headless --no-sandbox --disable-gpu  --metrics-recording-only --mute-audio --no-first-run --safebrowsing-disable-auto-update --disable-sync --disable-default-apps --disable-software-rasterizer --remote-debugging-port=${remoteDebugPort} &

python worker.py
