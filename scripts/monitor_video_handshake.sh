#!/bin/bash
# ==============================================================================
# Script Name: monitor_video_handshake.sh
# Description: Monitors active connections on RTMP (1935) and RTSP (8554).
#              Use this to confirm the drone has successfully connected.
# Version:     1.2.0
# Author:      System Architect (Gemini)
# Date:        2025-12-14
# ==============================================================================

# Configuration
# The Virtual IP of the Drone Controller (from your ZeroTier screenshot)
DRONE_IP="192.168.192.113" 

echo "================================================================"
echo "   📡  VIDEO LINK MONITOR (RTMP/RTSP)                           "
echo "   Waiting for connection from Controller: $DRONE_IP     "
echo "================================================================"

while true; do
    # 1. Check RTMP (Ingest) - This means the drone is UPLOADING video
    RTMP_LINK=$(netstat -an | grep "\.1935 " | grep "$DRONE_IP" | grep ESTABLISHED)

    # 2. Check RTSP (Output) - This means you are VIEWING video
    RTSP_LINK=$(netstat -an | grep "\.8554 " | grep ESTABLISHED)

    # Clear screen for dashboard view (optional, remove 'clear' if you want history)
    # clear 

    if [ ! -z "$RTMP_LINK" ]; then
        echo "🟢 [LIVE] Drone is STREAMING to Server (RTMP Connection Established)"
    else
        echo "🔴 [WAIT] Waiting for Drone Uplink..."
    fi

    if [ ! -z "$RTSP_LINK" ]; then
        echo "👀 [VIEW] A client (VLC/Grafana) is watching the stream."
    fi

    echo "----------------------------------------------------------------"
    sleep 2
done
