#!/bin/bash
# ==============================================================================
# Script Name: reset_db.sh
# Description: Wipes the DJI 'drone_telemetry' InfluxDB bucket to remove
#              bad or ghost data. Preserves Org, User, and Token settings.
#              Immediately recreates the bucket so the telemetry bridge has
#              somewhere to write without requiring a container restart.
# Version:     1.0.0
# Author:      RW
# Date:        2026-04-05
# ==============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# CONFIGURATION — override with environment variables if needed
# ---------------------------------------------------------------------------
CONTAINER="${INFLUX_CONTAINER:-dji_influx}"
ORG="${INFLUX_ORG:-dji_ops}"
BUCKET="${INFLUX_BUCKET:-drone_telemetry}"
TOKEN="${INFLUX_TOKEN:-my-super-secret-token-change-me}"

echo "================================================================"
echo "  DJI DATABASE RESET TOOL v1.0.0"
echo "  Container : $CONTAINER"
echo "  Org       : $ORG"
echo "  Bucket    : $BUCKET"
echo "================================================================"
echo ""
echo "⚠️  WARNING: This will PERMANENTLY DELETE all DJI flight data in '$BUCKET'."
echo "   Grafana will remain connected but charts will be empty until new"
echo "   telemetry arrives."
echo ""
read -r -p "   Type 'yes' to confirm: " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
    echo "❌ Aborted. No data was deleted."
    exit 0
fi

echo ""

# ---------------------------------------------------------------------------
# 1. Delete old bucket
# ---------------------------------------------------------------------------
echo "🗑️  Deleting bucket '$BUCKET'..."
docker exec "$CONTAINER" influx bucket delete \
    --name    "$BUCKET"    \
    --org     "$ORG"       \
    --token   "$TOKEN"

# ---------------------------------------------------------------------------
# 2. Recreate bucket immediately
# ---------------------------------------------------------------------------
echo "✨ Recreating clean bucket '$BUCKET'..."
docker exec "$CONTAINER" influx bucket create \
    --name        "$BUCKET"    \
    --org         "$ORG"       \
    --token       "$TOKEN"     \
    --description "Clean DJI telemetry storage — created $(date '+%Y-%m-%d %H:%M:%S')"

echo ""
echo "================================================================"
echo "✅ Database reset complete. You have a fresh start."
echo "   Restart the DJI telemetry bridge to begin writing new data."
echo "================================================================"
