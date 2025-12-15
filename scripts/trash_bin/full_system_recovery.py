import os
import time
import subprocess
import json
import sys
import urllib.request
import urllib.error
import base64

# ==============================================================================
# Script: full_system_recovery.py
# Version: 1.1.0 (Zero-Dependency Edition)
# Description: 
#   1. Generates valid, static configuration files (Fixes Video Crash).
#   2. Redeploys the container stack (Fixes Permissions).
#   3. Restores the Grafana dashboard using standard libraries (Fixes "Missing Dashboard").
# ==============================================================================

# --- PATHS & CONSTANTS ---
CONFIG_DIR = "config"
DOCKER_DIR = "docker"
DASHBOARD_FILE = "src/dashboards/autel_engineering_v2.json"
RECORDING_DIR = "recordings"
GRAFANA_URL = "http://localhost:3000"

def write_file(filepath, content):
    """Writes content to a file, ensuring the directory exists."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content.strip())
    print(f"   📄 Wrote valid config to: {filepath}")

def run_cmd(cmd):
    """Runs a shell command and checks for errors."""
    print(f"   > {cmd}")
    ret = subprocess.run(cmd, shell=True)
    if ret.returncode != 0:
        print(f"   ⚠️  Warning: Command failed: {cmd}")

def wait_for_service(url, timeout=45):
    """Polls a URL until it returns 200 OK (Using standard lib)."""
    print(f"   ⏳ Waiting for {url} to become available...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionResetError):
            pass
        time.sleep(2)
    return False

def push_dashboard_json():
    """Pushes local dashboard file to Grafana API using standard urllib."""
    print("♻️  Restoring Dashboard View...")
    
    if not os.path.exists(DASHBOARD_FILE):
        print(f"❌ ERROR: Dashboard file not found: {DASHBOARD_FILE}")
        return

    with open(DASHBOARD_FILE, "r") as f:
        data = json.load(f)
    
    # Force overwrite and reset ID to let Grafana assign a new one
    data["id"] = None 
    payload = {"dashboard": data, "overwrite": True}
    json_data = json.dumps(payload).encode('utf-8')
    
    # Credentials
    user = os.getenv("GRAFANA_USER", "admin")
    pwd = os.getenv("GRAFANA_PASS", "admin")
    auth_str = f"{user}:{pwd}"
    b64_auth = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
    
    # Request Construction
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {b64_auth}'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as r:
            if r.status == 200:
                print("✅ SUCCESS: Dashboard restored from file!")
            else:
                print(f"⚠️  Dashboard upload warning: {r.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"❌ API Error: {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

# --- 1. CONFIGURATION (Stable, Hardcoded Ports) ---
MEDIAMTX_CONFIG = """
api: yes
metrics: yes

# Disable internal listeners to avoid port conflicts with Bridge
rtmp: no
hls: yes
webrtc: yes

paths:
  all:
    # --- DVR ENABLED (Root Mode fixes permissions) ---
    record: yes
    recordFormat: fmp4
    recordPath: /recordings/%path/%Y-%m-%d_%H-%M-%S.mp4
    recordPartDuration: 1s
    recordDeleteAfter: 168h

    # --- TRANSMISSION ---
    source: publisher
    sourceOnDemand: no
    rtspTransport: tcp
    
    # HLS Transcoding (Ports Hardcoded 8554 for Stability)
    runOnReady: ffmpeg -i rtsp://localhost:8554/$RTSP_PATH -c:v copy -c:a copy -f hls -hls_time 1 -hls_list_size 3 -hls_flags delete_segments /hls/$RTSP_PATH.m3u8
    runOnReadyRestart: yes
"""

# --- 2. INFRASTRUCTURE (Root User & Volume Fixes) ---
DOCKER_COMPOSE = """
version: '3.8'
services:
  autel_rtsp:
    image: bluenviron/mediamtx:latest-ffmpeg
    container_name: autel_rtsp
    network_mode: "host"
    user: "0:0"  # <--- CRITICAL: Runs as Root to write to Mac SSD
    volumes:
      - ../config/mediamtx.yml:/mediamtx.yml
      - ../recordings:/recordings
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
      -c:v copy -c:a copy -f rtsp rtsp://127.0.0.1:8554/live/rtsp-drone1

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

def main():
    print("🚀 STARTING FULL SYSTEM RECOVERY (v0.9.9 RC)")
    
    # 1. Write Configs
    print("\n[1/4] Writing Configuration...")
    write_file(f"{CONFIG_DIR}/mediamtx.yml", MEDIAMTX_CONFIG)
    write_file(f"{DOCKER_DIR}/docker-compose.yml", DOCKER_COMPOSE)
    
    # 2. Prepare Storage
    print("\n[2/4] Preparing Storage...")
    if not os.path.exists(RECORDING_DIR):
        os.makedirs(RECORDING_DIR)
    os.chmod(RECORDING_DIR, 0o777)
    
    # 3. Clean & Deploy
    print("\n[3/4] Restarting Stack...")
    # Kill everything to clear port conflicts
    run_cmd("docker stop $(docker ps -aq) 2>/dev/null")
    run_cmd("docker rm -f $(docker ps -aq) 2>/dev/null")
    
    # Launch new stack
    if os.path.exists(".env"):
        run_cmd(f"docker compose --env-file .env -f {DOCKER_DIR}/docker-compose.yml up -d")
    else:
        print("❌ CRITICAL: .env file missing. Cannot start Docker.")
        sys.exit(1)
        
    # 4. Restore Dashboard
    print("\n[4/4] Waiting for services...")
    if wait_for_service(GRAFANA_URL):
        push_dashboard_json()
    else:
        print("❌ Timeout waiting for Grafana.")

    print("\n✅ RECOVERY COMPLETE.")
    print("   👉 Check video: rtsp://localhost:8554/live/rtsp-drone1")
    print("   👉 Check dashboard: http://localhost:3000")

if __name__ == "__main__":
    main()
