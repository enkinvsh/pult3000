#!/bin/bash
# Install kaset-remote-bot as launchd service
set -euo pipefail

PLIST="com.kaset-remote-bot.plist"
SRC="$(dirname "$0")/$PLIST"
DST="$HOME/Library/LaunchAgents/$PLIST"

mkdir -p "$HOME/projects/kaset-remote-bot/logs"

# Unload if already loaded
launchctl unload "$DST" 2>/dev/null || true

# Copy and load
cp "$SRC" "$DST"
launchctl load "$DST"

echo "✅ kaset-remote-bot installed and started"
echo "   Logs: ~/projects/kaset-remote-bot/logs/"
echo "   Stop: launchctl unload $DST"
