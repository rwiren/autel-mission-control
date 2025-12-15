import os
import subprocess
import time

# ==============================================================================
# Script: restore_system.py
# Type:   Incident Response / Rollback
# Goal:   Revert to v0.9.5 configuration to stop crash loops.
#         - Removes 'user: 0:0' (Root)
#         - Disables DVR Recording
#         - Restores standard volume mappings
# ==============================================================================

def run_cmd(cmd):
    """Executes shell commands and prints output."""
    print(f"   > {cmd}")
    os.system(cmd)

def write_file(path, content):
    """Overwrites configuration files with known-good safe versions."""
    print(f"   📄 Restoring {path}...")
    with open(path, "w") as f:
        f.write(content)

print("🚨 INITIATING SYSTEM ROLLBACK TO v0.9.5 (STABLE)...")

# 1. Stop the Bleeding (Kill crashing containers)
print("🛑 Stopping unstable services...")
run_cmd("docker stop autel_rtsp autel_bridge 2>/dev/null")
run_cmd("docker rm -f autel_rtsp autel_bridge 2>/dev/null")

# 2. Restore Safe Configuration (mediamtx.yml)
#    - Disables recording
#    - Removes fmp4 settings
SAFE_CONFIG = """
api: yes
metrics: yes
paths:
  all:
    record: no
    source: publisher
    sourceOnDemand: no
    rtspTransport: tcp
    runOnReady: ffmpeg -i rtsp://localhost:$RTSP_PORT/$RTSP_PATH -c:v copy -c:a copy -f hls -hls_time 1 -hls_list_size 3 -hls_flags delete_segments /hls/$RTSP_PATH.m3u8
    runOnReadyRestart: yes
"""
write_file("config/mediamtx.yml", SAFE_CONFIG.strip())

# 3. Restore Safe Infrastructure (docker-compose.yml)
#    - REMOVES 'user: 0:0' (Root Mode) which caused the crash
#    - REMOVES './recordings' volume mapping
SAFE_DOCKER = """
version: '3.8'
services:
  autel_rtsp:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: autel_rtsp
    network_mode: "host"
    volumes:
      - ../config/mediamtx.yml:/mediamtx.yml
    restart: unless-stopped
    environment:
      - MTX_PROTOCOLS=tcp
      - MTX_WEBRTCADDITIONALHOSTS=127.0.0.1

  autel_bridge:
    image: linuxserver/ffmpeg:latest
    container_name: autel_bridge
    network_mode: "host"
    restart: always
    depends_on:
      - autel_rtsp
    command: >
      -listen 1 -i rtmp://0.0.0.0:1935/live/rtmp-drone1
      -c:v copy -c:a copy -f rtsp rtsp://127.0.0.1:8554/live/rtmp-drone1

  autel_mqtt:
    image: eclipse-mosquitto:2.0
    container_name: autel_mqtt
    ports:
      - "${MQTT_PORT}:1883"
      - "9001:9001"
    volumes:
      - ../config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - autel_mqtt_data:/mosquitto/data
      - autel_mqtt_log:/mosquitto/log
    restart: unless-stopped

  autel_telegraf:
    image: telegraf:1.28
    container_name: autel_telegraf
    network_mode: "host"
    volumes:
      - ../config/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    environment:
      - INFLUX_TOKEN=${INFLUX_TOKEN}
      - INFLUX_ORG=${INFLUX_ORG}
      - INFLUX_BUCKET=${INFLUX_BUCKET}
    depends_on:
      - autel_influx
    restart: unless-stopped

  autel_influx:
    image: influxdb:2.7
    container_name: autel_influx
    ports:
      - "8086:8086"
    volumes:
      - autel_influx_data:/var/lib/influxdb2
      - autel_influx_config:/etc/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUX_USER}
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUX_PASS}
      - DOCKER_INFLUXDB_INIT_ORG=${INFLUX_ORG}
      - DOCKER_INFLUXDB_INIT_BUCKET=${INFLUX_BUCKET}
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUX_TOKEN}
    restart: unless-stopped

  autel_grafana:
    image: grafana/grafana-oss:latest
    container_name: autel_grafana
    ports:
      - "3000:3000"
    volumes:
      - autel_grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASS}
      - GF_PANELS_DISABLE_SANITIZE_HTML=true
    restart: unless-stopped

volumes:
  autel_influx_data:
  autel_influx_config:
  autel_grafana_data:
  autel_mqtt_data:
  autel_mqtt_log:
"""
write_file("docker/docker-compose.yml", SAFE_DOCKER.strip())

# 4. Deployment
print("🚀 Redeploying Clean Stack...")
# Load env vars manually for python environment if needed, mostly for subshell
if os.path.exists(".env"):
    print("   ✅ Loading .env...")
else:
    print("   ⚠️  Warning: .env file missing")

run_cmd("docker compose --env-file .env -f docker/docker-compose.yml up -d autel_rtsp autel_bridge")

# 5. Verification
print("⏳ Waiting 5s for stability check...")
time.sleep(5)
print("\n📊 FINAL STATUS:")
os.system("docker ps | grep autel_")
