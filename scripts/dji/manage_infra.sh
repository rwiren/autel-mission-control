#!/bin/bash
# ==============================================================================
# Script Name: manage_infra.sh
# Description: Utility for starting, stopping, and verifying the Docker
#              infrastructure required for DJI mission control:
#              MQTT Broker (Mosquitto), InfluxDB, Grafana.
#              Mirrors scripts/manage_infra.sh but targets the DJI stack.
# Version:     1.0.0
# Author:      RW
# Date:        2026-04-05
# ==============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
DOCKER_COMPOSE_FILE="./docker/docker-compose.yml"
ENV_FILE=".env"

# ---------------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo -e "${GREEN}[DJI] Starting Infrastructure Reset...${NC}"

# ---------------------------------------------------------------------------
# 1. Verify Docker is running
# ---------------------------------------------------------------------------
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}[ERROR] Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Tear down existing containers (removes orphans from previous versions)
# ---------------------------------------------------------------------------
echo -e "${GREEN}[DJI] Stopping legacy containers...${NC}"
docker compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans

# ---------------------------------------------------------------------------
# 3. Start services in detached mode
# ---------------------------------------------------------------------------
echo -e "${GREEN}[DJI] Starting services (InfluxDB, Mosquitto, Grafana)...${NC}"
docker compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# ---------------------------------------------------------------------------
# 4. Health check — wait for MQTT broker on port 1883 (up to 30 s)
# ---------------------------------------------------------------------------
echo -e "${GREEN}[DJI] Waiting for MQTT Broker on port 1883...${NC}"
for i in $(seq 1 30); do
    if nc -z localhost 1883 2>/dev/null; then
        echo -e "${GREEN}[SUCCESS] MQTT Broker is ONLINE.${NC}"
        break
    fi
    echo "   Waiting... (${i}/30)"
    sleep 1
done

# ---------------------------------------------------------------------------
# 5. Print running containers
# ---------------------------------------------------------------------------
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "${GREEN}[DJI] Infrastructure ready. You may now start the DJI telemetry bridge.${NC}"
