#!/bin/bash
set -euo pipefail

REPO="https://github.com/enkinvsh/pult3000.git"
DIR="$HOME/pult3000"

echo "=== Pult3000 Installer ==="

# Clone
if [ -d "$DIR" ]; then
    echo "Updating existing installation..."
    cd "$DIR" && git pull
else
    echo "Cloning repo..."
    git clone "$REPO" "$DIR"
fi

cd "$DIR"

# Create .env if missing
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env config..."
    read -p "Telegram Bot Token: " BOT_TOKEN
    read -p "Your Telegram User ID: " ADMIN_ID
    read -p "Proxy URL (leave empty if not needed): " PROXY_URL
    
    cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
EOF
    [ -n "$PROXY_URL" ] && echo "PROXY_URL=$PROXY_URL" >> .env
    echo ".env created"
fi

# Setup venv
echo "Setting up Python environment..."
python3 -m venv .venv
.venv/bin/pip install -q -e .

# Install Playwright browser
echo "Installing Chromium for Playwright..."
.venv/bin/playwright install chromium

# Install launchd service
echo "Installing service..."
bash deploy/install.sh

echo ""
echo "=== Done! ==="
echo "Logs: $DIR/logs/"
echo "Stop: launchctl unload ~/Library/LaunchAgents/com.pult3000.plist"
