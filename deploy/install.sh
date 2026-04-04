#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_NAME="com.kaset-remote-bot.plist"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"
VENV="$DIR/.venv"
PYTHON="${VENV}/bin/python"

# Create venv if missing
if [ ! -f "$PYTHON" ]; then
    echo "Creating venv..."
    python3.13 -m venv "$VENV" 2>/dev/null || python3 -m venv "$VENV"
fi

# Install/update deps
echo "Installing dependencies..."
"$VENV/bin/pip" install -q -e "$DIR"

# Create logs dir, truncate if > 10MB
mkdir -p "$DIR/logs"
for log in "$DIR/logs"/*.log; do
    [ -f "$log" ] && [ "$(stat -f%z "$log" 2>/dev/null || echo 0)" -gt 10485760 ] && : > "$log"
done

# Generate plist with correct paths
cat > "$DIR/deploy/$PLIST_NAME" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kaset-remote-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>-m</string>
        <string>src.main</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${DIR}/logs/bot.log</string>
    <key>StandardErrorPath</key>
    <string>${DIR}/logs/bot.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
PLIST

# Stop if running
launchctl unload "$PLIST_DST" 2>/dev/null || true

# Install and start
cp "$DIR/deploy/$PLIST_NAME" "$PLIST_DST"
launchctl load "$PLIST_DST"

echo "✅ kasset-remote started"
echo "   Logs: $DIR/logs/"
echo "   Stop: launchctl unload $PLIST_DST"
