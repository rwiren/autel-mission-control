#!/bin/bash
# ==============================================================================
# SCRIPT: restore_system.sh
# VERSION: 1.0.0
# DESCRIPTION: Performs a "Factory Reset" on the Docker infrastructure.
#              1. Stops all containers.
#              2. REMOVES DATA VOLUMES (Fixes password/token mismatches).
#              3. Rebuilds and starts the full stack (Telemetry + Video).
# ==============================================================================

echo "🛑 STOPPING SERVICES..."
docker compose -f docker/docker-compose.yml down

echo "🧹 CLEANING STALE VOLUMES (Fixing Auth Conflicts)..."
# This deletes the database data so it regenerates with the correct Token
docker volume rm docker_influxdb_data docker_influxdb_config docker_grafana_data 2>/dev/null

echo "🕵️ VERIFYING DRONE CONNECTION..."
# Quick ping check to see if the controller is reachable
if ping -c 1 192.168.1.201 &> /dev/null; then
    echo "   ✅ Controller (192.168.1.201) is ONLINE."
else
    echo "   ⚠️  Controller (192.168.1.201) is UNREACHABLE."
    echo "       Please ensure you are connected to the Drone's Wi-Fi."
fi

echo "🚀 BUILDING & STARTING PRODUCTION STACK..."
docker compose -f docker/docker-compose.yml up -d --build

echo "⏳ WAITING FOR DATABASE INITIALIZATION (10s)..."
sleep 10

echo "📋 SYSTEM STATUS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🔍 CHECKING INGESTOR LOGS (Recent Activity):"
docker logs --tail 10 autel_ingestor

echo "==================================================="
echo "✅ RESTORE COMPLETE."
echo "   - Dashboard: http://localhost:3000"
echo "   - Username: admin / Password: R!ku3404"
echo "==================================================="
