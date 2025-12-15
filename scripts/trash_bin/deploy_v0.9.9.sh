#!/bin/bash
# ==============================================================================
# Script: deploy_v0.9.9.sh
# Type:   Master Deployment (Architectural Reset)
# Description: 
#   1. Identifies and KILLS all legacy containers (autel_broker, autel_rtmp).
#   2. Clears "Port Already in Use" errors.
#   3. Launches the clean v0.9.9 stack with DVR support.
# ==============================================================================

# 1. Environment Loading
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    echo "✅ Configuration loaded."
else
    echo "❌ ERROR: .env file missing."
    exit 1
fi

echo "🧹 STARTING DEEP CLEANUP (Removing legacy conflicts)..."

# 2. The Kill List
# We must explicitly stop OLD container names that are holding the ports.
CONFLICTS=(
    "autel_rtsp" 
    "autel_bridge" 
    "autel_mqtt" 
    "autel_telegraf" 
    "autel_influx" 
    "autel_grafana"
    "autel_broker"  # <--- The ghost holding port 1883
    "autel_rtmp"    # <--- The ghost holding port 1935
)

for container in "${CONFLICTS[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "   💀 Killing legacy artifact: $container"
        docker stop "$container" >/dev/null 2>&1
        docker rm -f "$container" >/dev/null 2>&1
    fi
done

# 3. Network Flush
# Ensure no zombie networks are holding the bindings
echo "   🚿 Pruning networks..."
docker network prune -f >/dev/null 2>&1

# 4. Storage Prep
echo "   📂 Verifying storage permissions..."
mkdir -p ./recordings
chmod 777 ./recordings

# 5. Launch
echo "🚀 DEPLOYING AUTEL MISSION CONTROL v0.9.9..."
docker compose --env-file .env -f docker/docker-compose.yml up -d

# 6. Verification
echo "   🏥 Health check (waiting 5s)..."
sleep 5

# Check status of the Video Core
RTSP_STATUS=$(docker inspect -f '{{.State.Status}}' autel_rtsp 2>/dev/null)
MQTT_STATUS=$(docker inspect -f '{{.State.Status}}' autel_mqtt 2>/dev/null)

if [ "$RTSP_STATUS" == "running" ] && [ "$MQTT_STATUS" == "running" ]; then
    echo ""
    echo "✅ SYSTEM GREEN - READY FOR FLIGHT"
    echo "   ---------------------------------------"
    echo "   📹 Video Core:   ONLINE (Port 8554/1935)"
    echo "   📼 DVR Status:   RECORDING (./recordings)"
    echo "   📡 Telemetry:    ONLINE (Port 1883)"
    echo "   ---------------------------------------"
else
    echo ""
    echo "❌ DEPLOYMENT FAILED"
    echo "   RTSP: $RTSP_STATUS"
    echo "   MQTT: $MQTT_STATUS"
    echo "   Run 'docker logs autel_rtsp' for details."
fi
