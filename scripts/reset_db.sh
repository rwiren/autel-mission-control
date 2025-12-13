#!/bin/bash
# ==============================================================================
# SCRIPT: reset_db.sh
# VERSION: 1.0.0
# DESCRIPTION: Wipes the 'telemetry' bucket to remove bad/ghost data.
#              Preserves Org, User, and Token settings.
# ==============================================================================

CONTAINER="autel_influx"
ORG="autel_ops"
BUCKET="telemetry"
TOKEN="my-super-secret-token-change-me"

echo "⚠️  WARNING: This will PERMANENTLY DELETE all flight data in '$BUCKET'."
echo "    The Grafana connection will remain valid, but charts will go empty."
echo "----------------------------------------------------------------"

# 1. DELETE OLD BUCKET
echo "🗑️  Deleting bucket '$BUCKET'..."
docker exec $CONTAINER influx bucket delete \
  --name $BUCKET \
  --org $ORG \
  --token $TOKEN

# 2. CREATE NEW BUCKET
# We recreate it immediately so the Bridge has somewhere to write.
echo "✨ Recreating clean bucket '$BUCKET'..."
docker exec $CONTAINER influx bucket create \
  --name $BUCKET \
  --org $ORG \
  --token $TOKEN \
  --description "Clean telemetry storage created on $(date)"

echo "----------------------------------------------------------------"
echo "✅ Database Reset Complete. You have a fresh start."
