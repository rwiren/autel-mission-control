#!/bin/bash
# ==============================================================================
# Script: upgrade_to_dvr_v2.sh
# Version: 0.9.8.1 (Hotfix: Conflict & Env Loader)
# Description: Forcefully replaces the video container with the DVR version.
# ==============================================================================

# 1. Load Environment Variables (Fixes the WARN messages)
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    echo "✅ Loaded environment variables from .env"
else
    echo "❌ ERROR: .env file not found! Please create it first."
    exit 1
fi

echo "🎥 Autel Mission Control: Enabling DVR (Black Box)..."

# 2. Create the Landing Zone
RECORDING_DIR="./recordings"
mkdir -p "$RECORDING_DIR"
chmod 777 "$RECORDING_DIR"
echo "   📂 Storage prepared at: $RECORDING_DIR"

# 3. Force Kill the Old Container (Fixes the Conflict error)
echo "   💀 Killing old video relay..."
docker stop autel_rtsp 2>/dev/null
docker rm -f autel_rtsp 2>/dev/null

# 4. Launch the New DVR Container
echo "   🚀 Launching Black Box Recorder..."
docker compose --env-file .env -f docker/docker-compose.yml up -d autel_rtsp

# 5. Verification
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DVR ACTIVE!"
    echo "   --------------------------------------------------------"
    echo "   🔴 Recording Status: READY"
    echo "   📂 Location: $RECORDING_DIR"
    echo "   --------------------------------------------------------"
else
    echo "❌ CRITICAL FAILURE: Docker refused to start."
fi
