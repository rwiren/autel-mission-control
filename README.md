# Autel Mission Control - Video & Telemetry Hub

**Version:** v0.9.1
**Architecture:** Microservices (Dual-Lane)

A centralized mission control server for Autel drones, running on Docker. It provides real-time video streaming (RTSP/RTMP) and telemetry logging (InfluxDB/Grafana).

## 🚀 Key Features
* **Dual-Lane Video:** Supports both **RTSP** (Low Latency) and **RTMP** (High Reliability) simultaneously.
* **Mac/Docker Optimized:** Fixes UDP packet loss issues on Apple Silicon using a TCP-locked architecture.
* **Auto-Sanitization:** Automatically cleans "garbage" metadata from Autel RTMP streams using a dedicated bridge.
* **Dashboard Ready:** Outputs WebRTC and HLS for browser-based ground stations.

## 📡 Connection Lanes

### Lane 1: RTSP (Fast Lane)
Use this for the lowest latency. Connects directly to the main server.
* **Controller URL:** `rtsp://<YOUR_IP>:8554/live/rtsp-drone1`
* **VLC Playback:** `rtsp://<YOUR_IP>:8554/live/rtsp-drone1`

### Lane 2: RTMP (Stable Lane)
Use this if RTSP is unstable. Goes through a cleaning layer (NGINX -> FFmpeg).
* **Controller URL:** `rtmp://<YOUR_IP>:1935/live/rtmp-drone1`
* **VLC Playback:** `rtmp://<YOUR_IP>:1936/live/rtmp-drone1` *(Note port 1936)*

### Dashboard (Browser)
* **RTSP Feed:** `http://<YOUR_IP>:8889/live/rtsp-drone1`
* **RTMP Feed:** `http://<YOUR_IP>:8889/live/rtmp-drone1`

## 🛠️ Quick Start

1.  **Configure Environment:**
    Ensure `.env` contains your IP and credentials.
    ```bash
    MQTT_PORT=1883
    GRAFANA_USER=admin
    GRAFANA_PASS=admin
    INFLUX_USER=admin
    INFLUX_PASS=adminpassword
    INFLUX_ORG=autel
    INFLUX_BUCKET=telemetry
    INFLUX_TOKEN=my-super-secret-token
    ```

2.  **Launch Stack:**
    ```bash
    docker compose --env-file .env -f docker/docker-compose.yml up -d
    ```

3.  **Verify Status:**
    Run `docker ps`. You should see `autel_rtsp`, `autel_rtmp`, and `autel_bridge` running.
