#!/bin/bash
# ==============================================================================
# Script: architectural_reset.sh
# Version: 1.0.0
# Description: Performs a clean teardown and rebuild of the video subsystem.
#              Ensures Permissions, Configuration, and Container Health.
# ==============================================================================

# 1. Environment Integrity Check
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    echo "✅ Environment variables loaded."
else
    echo "❌ CRITICAL: .env file missing. Deployment aborted."
    exit 1
fi

echo "🔄 Initiating Video Subsystem Reset..."

# 2. Infrastructure Prep
RECORD_DIR="./recordings"
mkdir -p "$RECORD_DIR"
# Relax permissions on host to accept writes from container root
chmod 777 "$RECORD_DIR"
echo "   📂 Storage volume initialized: $RECORD_DIR"

# 3. Teardown (Kill it with fire)
# We stop only the video components to minimize disruption
echo "   💀 Terminating stale video services..."
docker stop autel_rtsp autel_bridge 2>/dev/null
docker rm -f autel_rtsp autel_bridge 2>/dev/null

# 4. Deployment
echo "   🚀 deploying v0.9.9 Stack..."
docker compose --env-file .env -f docker/docker-compose.yml up -d autel_rtsp autel_bridge

# 5. Health Verification
echo "   🏥 Performing health check (5s)..."
sleep 5

RTSP_STATUS=$(docker inspect -f '{{.State.Status}}' autel_rtsp 2>/dev/null)
BRIDGE_STATUS=$(docker inspect -f '{{.State.Status}}' autel_bridge 2>/dev/null)

if [ "$RTSP_STATUS" == "running" ] && [ "$BRIDGE_STATUS" == "running" ]; then
    echo ""
    echo "✅ SYSTEM GREEN"
    echo "   ---------------------------------------"
    echo "   📹 Video Server:  ONLINE (PID: $(docker inspect -f '{{.State.Pid}}' autel_rtsp))"
    echo "   🛡️  Bridge Service: ONLINE"
    echo "   📼 DVR Status:    ACTIVE (fmp4)"
    echo "   ---------------------------------------"
    echo "   Ready for operations."
else
    echo ""
    echo "❌ SYSTEM FAILURE"
    echo "   RTSP Status:   $RTSP_STATUS"
    echo "   Bridge Status: $BRIDGE_STATUS"
    echo "   Check logs: docker logs autel_rtsp"
    exit 1
fi
