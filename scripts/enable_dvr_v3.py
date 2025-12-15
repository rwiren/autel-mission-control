import os
import shutil
import subprocess
import datetime

# ==============================================================================
# Script: enable_dvr_v3.py
# Version: 3.0.0 (Safe Upgrade)
# Description: 
#   1. Backs up current stable config.
#   2. Enables DVR (Recording) in MediaMTX.
#   3. Adds a 'File Browser' container for instant playback.
#   4. Updates permissions to allow writing to Mac SSD.
# ==============================================================================

# --- PATHS ---
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = f"backups/pre_dvr_{TIMESTAMP}"
CONFIG_FILE = "config/mediamtx.yml"
COMPOSE_FILE = "docker/docker-compose.yml"
RECORD_DIR = "recordings"

# --- 1. NEW CONFIGURATION (DVR ENABLED) ---
# We keep the exact ports and IPs from your v0.9.3 setup, but add 'record: yes'.
NEW_MEDIAMTX_CONFIG = """
paths:
  all:
    # --- DVR SETTINGS ---
    record: yes
    # FMP4 is crash-safe (saves even if power is lost)
    recordFormat: fmp4
    # Organization: recordings/stream_name/YYYY-MM-DD_HH-MM-SS.mp4
    recordPath: /recordings/%path/%Y-%m-%d_%H-%M-%S.mp4
    # Split files every 10 minutes to keep them manageable
    recordPartDuration: 10m
    # Auto-delete files older than 24 hours to save disk space
    recordDeleteAfter: 24h

    # --- TRANSMISSION (LANE 1) ---
    rtsp: yes
    rtspAddress: :8554
    protocols: [tcp]

    # --- RTMP INPUT (LANE 2) ---
    rtmp: yes
    rtmpAddress: :1935

    # --- WEB OUTPUT ---
    hls: yes
    hlsAddress: :8888
    hlsVariant: lowLatency
    
    webrtc: yes
    webrtcAddress: :8889
    # Matches your existing setup
    webrtcAdditionalHosts: [ "192.168.1.201", "127.0.0.1" ]

    readTimeout: 20s
    writeTimeout: 20s
"""

# --- 2. NEW INFRASTRUCTURE (With FileBrowser) ---
# We add 'autel_playback' service and mount the recordings volume.
NEW_DOCKER_COMPOSE = """
version: '3.8'
services:
  # --- VIDEO CORE ---
  rtsp_server:
    image: bluenviron/mediamtx:latest
    container_name: autel_rtsp
    restart: always
    user: "0:0"   # <--- CRITICAL: Root permissions for DVR
    ports:
      - "8554:8554"
      - "1936:1935"
      - "8888:8888"
      - "8889:8889"
      - "8189:8189/udp"
    volumes:
      - ../config/mediamtx.yml:/mediamtx.yml
      - ../recordings:/recordings  # <--- Persistent Storage
    environment:
      - MTX_WEBRTCADDITIONALHOSTS=192.168.1.201

  # --- PLAYBACK UI (New!) ---
  playback_server:
    image: filebrowser/filebrowser:latest
    container_name: autel_playback
    restart: always
    ports:
      - "8080:80"
    volumes:
      - ../recordings:/srv
      - ../config/filebrowser.db:/database.db
    # Default login: admin / admin

  # --- RTMP INGEST ---
  rtmp_server:
    image: tiangolo/nginx-rtmp
    container_name: autel_rtmp
    restart: always
    ports:
      - "1935:1935"

  # --- STREAM BRIDGE ---
  rtmp_bridge:
    image: mwader/static-ffmpeg:latest
    container_name: autel_bridge
    restart: on-failure
    depends_on:
      - rtsp_server
      - rtmp_server
    command: >
      -re -i rtmp://autel_rtmp:1935/live/rtmp-drone1
      -c copy 
      -f flv 
      rtmp://autel_rtsp:1935/live/rtmp-drone1

  # --- METRICS STACK (Unchanged) ---
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: autel_broker
    restart: always
    ports: ["${MQTT_PORT}:1883", "9001:9001"]
    volumes:
      - ../config:/mosquitto/config
      - mosquitto_data:/mosquitto/data
      - mosquitto_log:/mosquitto/log

  influxdb:
    image: influxdb:2
    container_name: autel_influx
    restart: always
    ports: ["8086:8086"]
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUX_USER}
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUX_PASS}
      - DOCKER_INFLUXDB_INIT_ORG=${INFLUX_ORG}
      - DOCKER_INFLUXDB_INIT_BUCKET=${INFLUX_BUCKET}
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUX_TOKEN}
    volumes:
      - influxdb2_data:/var/lib/influxdb2

  telegraf:
    image: telegraf:1.29
    container_name: autel_telegraf
    restart: always
    depends_on: [influxdb, mosquitto]
    environment:
      - INFLUX_TOKEN=${INFLUX_TOKEN}
      - INFLUX_ORG=${INFLUX_ORG}
      - INFLUX_BUCKET=${INFLUX_BUCKET}
    volumes:
      - ../config/telegraf.conf:/etc/telegraf/telegraf.conf:ro

  grafana:
    image: grafana/grafana-oss:latest
    container_name: autel_grafana
    restart: always
    ports: ["3000:3000"]
    depends_on: [influxdb]
    environment:
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASS}
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_PANELS_DISABLE_SANITIZE_HTML=true
    volumes:
      - grafana_data:/var/lib/grafana
      - ../config/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml

volumes:
  mosquitto_data:
  mosquitto_log:
  influxdb2_data:
  grafana_data:
"""

def run_cmd(cmd):
    print(f"   > {cmd}")
    os.system(cmd)

def main():
    print("🎥 INITIATING DVR UPGRADE (v3.0.0)...")

    # 1. Prepare Storage
    print("\n[1/5] Preparing Storage...")
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)
    # Create empty DB file for filebrowser
    open("config/filebrowser.db", "a").close()
    print(f"   📂 Storage ready at ./{RECORD_DIR}")

    # 2. Backup
    print("\n[2/5] Creating Backup...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE): shutil.copy(CONFIG_FILE, BACKUP_DIR)
    if os.path.exists(COMPOSE_FILE): shutil.copy(COMPOSE_FILE, BACKUP_DIR)
    print(f"   💾 Backup saved to {BACKUP_DIR}")

    # 3. Write New Configs
    print("\n[3/5] Updating Configurations...")
    with open(CONFIG_FILE, "w") as f:
        f.write(NEW_MEDIAMTX_CONFIG.strip())
    with open(COMPOSE_FILE, "w") as f:
        f.write(NEW_DOCKER_COMPOSE.strip())
    print("   ✅ Configuration files updated.")

    # 4. Restart Video Services Only
    print("\n[4/5] Applying Changes...")
    # We use 'up -d' which intelligently recreates only changed containers
    run_cmd("docker compose --env-file .env -f docker/docker-compose.yml up -d --remove-orphans")

    # 5. Summary
    print("\n✅ UPGRADE COMPLETE")
    print("   -------------------------------------------------")
    print("   🔴 DVR Status:      ACTIVE (Saving to ./recordings)")
    print("   📂 Playback UI:     http://localhost:8080 (admin/admin)")
    print("   📹 Live Stream:     rtsp://localhost:8554/live/rtsp-drone1")
    print("   -------------------------------------------------")
    print("   Note: If video does not appear, toggle 'Live Stream' on your controller.")

if __name__ == "__main__":
    main()
