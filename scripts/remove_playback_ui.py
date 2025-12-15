import os
import subprocess
import shutil

# ==============================================================================
# Script: remove_playback_ui.py
# Purpose: Removes the 'playback_server' (FileBrowser) from the stack.
#          preserves the DVR recording capability in the RTSP server.
# ==============================================================================

COMPOSE_FILE = "docker/docker-compose.yml"
BACKUP_FILE = "docker/docker-compose.yml.bak"

# This is your Clean, Stable Architecture (v3.1.0) without the FileBrowser
CLEAN_COMPOSE_CONTENT = """
version: '3.8'
services:
  # --- VIDEO CORE (DVR HANDLED HERE) ---
  rtsp_server:
    image: bluenviron/mediamtx:latest
    container_name: autel_rtsp
    restart: always
    user: "0:0"   # Root required for writing recordings
    ports:
      - "8554:8554"
      - "1936:1935"
      - "8888:8888"
      - "8889:8889"
      - "8189:8189/udp"
    volumes:
      - ../config/mediamtx.yml:/mediamtx.yml
      - ../recordings:/recordings  # <--- Video saved here locally
    environment:
      - MTX_WEBRTCADDITIONALHOSTS=192.168.1.201

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

  # --- METRICS STACK ---
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

def main():
    print("✂️  REMOVING PLAYBACK UI (v3.1.0)...")

    # 1. Stop the Annoying Container
    print("\n[1/3] Stopping Playback Container...")
    subprocess.run("docker stop autel_playback", shell=True)
    subprocess.run("docker rm autel_playback", shell=True)
    print("   ✅ Container removed.")

    # 2. Update Infrastructure Config
    print("\n[2/3] Updating Architecture...")
    # Backup first
    if os.path.exists(COMPOSE_FILE):
        shutil.copy(COMPOSE_FILE, BACKUP_FILE)
    
    # Write Clean Config
    with open(COMPOSE_FILE, "w") as f:
        f.write(CLEAN_COMPOSE_CONTENT.strip())
    print("   ✅ docker-compose.yml updated (Service removed).")

    # 3. Clean Restart of Core
    print("\n[3/3] Stabilizing Core Systems...")
    # This ensures the rest of the stack knows the other guy is gone
    subprocess.run("docker compose --env-file .env -f docker/docker-compose.yml up -d --remove-orphans", shell=True)

    print("\n✅ DONE.")
    print("   -------------------------------------------------")
    print("   🌐 Dashboard:    http://localhost:3000")
    print("   📹 Recordings:   Located in your folder 'autel-mission-control/recordings'")
    print("   -------------------------------------------------")
    print("   To view videos, simply open the folder in Finder!")

if __name__ == "__main__":
    main()
