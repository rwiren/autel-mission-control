#!/bin/bash
# -----------------------------------------------------------------------------
# Script Name: manage_infra.sh
# Description: System Architect utility to reset and verify Docker infrastructure.
# Version:     1.0.0
# Author:      System Architect (Gemini)
# Date:        2025-12-14
# -----------------------------------------------------------------------------

# Configuration
DOCKER_COMPOSE_FILE="./docker/docker-compose.yml"
ENV_FILE=".env"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[SYSTEM] Starting Infrastructure Reset...${NC}"

# 1. Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}[ERROR] Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# 2. Tear down existing containers (removes orphans from previous versions)
echo -e "${GREEN}[SYSTEM] Stopping legacy containers...${NC}"
docker compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans

# 3. Start services in detached mode
echo -e "${GREEN}[SYSTEM] Starting services (InfluxDB, Mosquitto, Grafana)...${NC}"
docker compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# 4. Health Check - Wait for Mosquitto port 1883
echo -e "${GREEN}[SYSTEM] Waiting for MQTT Broker on port 1883...${NC}"
for i in {1..30}; do
    if nc -z localhost 1883; then
        echo -e "${GREEN}[SUCCESS] MQTT Broker is ONLINE.${NC}"
        break
    fi
    echo "Waiting..."
    sleep 1
done

# 5. Show running containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "${GREEN}[SYSTEM] Infrastructure Ready. You may now run bridge.py.${NC}"
