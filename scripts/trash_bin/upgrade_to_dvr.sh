#!/bin/bash
# ==============================================================================
# Script: upgrade_to_dvr.sh
# Version: 0.9.8
# Description: Prepares the host for DVR recording and restarts video services.
# ==============================================================================

echo "🎥 Autel Mission Control: Enabling DVR (Black Box)..."

# 1. Create the Landing Zone
RECORDING_DIR="./recordings"

if [ ! -d "$RECORDING_DIR" ]; then
    echo "   Creating directory: $RECORDING_DIR"
    mkdir -p "$RECORDING_DIR"
else
    echo "   ✅ Recording directory exists."
fi

# 2. Set Permissions (Crucial for Docker)
# We make it writable so the container user (often root or nobody) can write mp4s.
echo "   🔓 Setting permissions on $RECORDING_DIR..."
chmod 777 "$RECORDING_DIR"

# 3. Restart Video Services Only
# We don't need to restart database/grafana, just the video pipe.
echo "   🔄 Restarting Video Relay (autel_rtsp)..."
docker compose -f docker/docker-compose.yml up -d --force-recreate autel_rtsp

echo ""
echo "✅ DVR UPGRADE COMPLETE!"
echo "   --------------------------------------------------------"
echo "   📂 Videos will appear in: $RECORDING_DIR/live/rtsp-drone1/"
echo "   💾 Format: fmp4 (Safe against power loss)"
echo "   🧹 Retention: 7 Days"
echo "   --------------------------------------------------------"
echo "   Ready for takeoff. 🛸"
