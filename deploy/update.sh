#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

echo "Pulling latest..."
git pull --ff-only

echo "Restarting..."
bash "$DIR/deploy/install.sh"
