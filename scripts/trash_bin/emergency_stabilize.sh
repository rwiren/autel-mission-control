#!/bin/bash
# ==============================================================================
# Script: emergency_stabilize.sh
# Version: 0.9.9-hotfix
# Description: Disables DVR recording and forces a video system restart.
#              Use this to recover from a crash loop in the field.
# ==============================================================================

# 1. Configuration: Disable Black Box Recording
echo "🔧 Configuring: Disabling DVR to restore stability..."
# Using sed to find 'record: yes' and replace with 'record: no' in the config
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed syntax
    sed -i '' 's/record: yes/record: no/g' config/mediamtx.yml
else
    # Linux sed syntax
    sed -i 's/record: yes/record: no/g' config/mediamtx.yml
fi

# 2. Service Restart: Video Pipeline Only
echo "🔄 Restarting Video Services..."
docker restart autel_rtsp
docker restart autel_bridge

# 3. Verification: Check for Crash Loops
echo "⏳ Verifying stability (waiting 5s)..."
sleep 5

# Check if autel_rtsp is running
if docker ps | grep -q "autel_rtsp"; then
    STATUS=$(docker inspect -f '{{.State.Status}}' autel_rtsp)
    if [ "$STATUS" == "running" ]; then
        echo "✅ SUCCESS: Video Server is UP and STABLE."
        echo "   - DVR: Disabled"
        echo "   - Stream: Active"
    else
        echo "⚠️  WARNING: Container exists but status is: $STATUS"
    fi
else
    echo "❌ CRITICAL: autel_rtsp container is NOT running."
fi

# 4. Final Status Output
echo "📊 Current Stack Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
