#!/bin/bash
# ==============================================================================
# Script: deploy_mission_control.sh
# Version: v0.9.9 (Final)
# Description: Single-command deployment for the Autel Mission Control Stack.
#              - Loads Environment
#              - Prepares Storage
#              - Cleans Old Containers
#              - Launches Full Stack
# ==============================================================================

# 1. Load Environment Variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    echo "✅ Configuration loaded from .env"
else
    echo "❌ ERROR: .env file missing. Cannot deploy."
    exit 1
fi

echo "🚀 Deploying Autel Mission Control v0.9.9..."

# 2. Prepare DVR Storage
RECORD_DIR="./recordings"
mkdir -p "$RECORD_DIR"
# Ensure it's writable (though the container is now Root, this is good practice)
chmod 777 "$RECORD_DIR"
echo "   📂 Black Box Storage: $RECORD_DIR"

# 3. Clean Slate (Stop & Remove Old Containers)
echo "   🧹 Cleaning up previous deployment..."
docker stop autel_rtsp autel_bridge autel_mqtt autel_telegraf autel_influx autel_grafana 2>/dev/null
docker rm -f autel_rtsp autel_bridge autel_mqtt autel_telegraf autel_influx autel_grafana 2>/dev/null

# 4. Launch Stack
echo "   🔥 Igniting Microservices..."
docker compose --env-file .env -f docker/docker-compose.yml up -d

# 5. Verification
echo "   🏥 Waiting for system stabilization (5s)..."
sleep 5

# Check if Video Core is alive (The most critical part)
RTSP_STATUS=$(docker inspect -f '{{.State.Status}}' autel_rtsp 2>/dev/null)

if [ "$RTSP_STATUS" == "running" ]; then
    echo ""
    echo "✅ MISSION CONTROL ONLINE"
    echo "   ---------------------------------------"
    echo "   📹 Video Feed:   rtsp://localhost:8554/live/rtsp-drone1"
    echo "   📼 Black Box:    Recording Active (fmp4)"
    echo "   📊 Dashboard:    http://localhost:3000"
    echo "   ---------------------------------------"
else
    echo "❌ DEPLOYMENT FAILED: Video Core is $RTSP_STATUS"
    docker logs autel_rtsp
    exit 1
fi
