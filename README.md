# 🚁 Autel Mission Control

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Docker%20%7C%20Mac%20Silicon-lightgrey.svg)]()
![Last Updated](https://img.shields.io/github/last-commit/rwiren/autel-mission-control?label=Last%20Updated&color=orange)

> **A centralized mission control hub for Autel drones, delivering specialized dual-lane real-time video streaming and comprehensive telemetry logging via Docker.**

---

### 📢 🆕 Latest Updates: v0.9.1 released!
**[Click here to view the RELEASENOTES.md for detailed changelogs and architecture shifts.](RELEASENOTES.md)**

---

## 📖 Table of Contents
1.  [Project Overview](#-project-overview)
2.  [Key Features](#-key-features)
3.  [System Architecture](#%EF%B8%8F-system-architecture)
4.  [Connection Lanes & Usage](#-connection-lanes--usage)
5.  [Quick Start Deployment](#%EF%B8%8F-quick-start-deployment)

## 🔭 Project Overview

**Autel Mission Control** is designed to overcome specific challenges when integrating Autel drone video feeds into modern network environments, particularly on macOS and Docker. It provides a robust backend for ground station software, handling video ingestion, sanitization, and redistribution alongside real-time metric data storage.

## 🚀 Key Features

* 🎥 **Dual-Lane Video Architecture:** Simultaneously supports low-latency **RTSP (TCP-locked)** for speed and high-reliability **RTMP** for challenging connection environments.
* 🛡️ **Auto-Sanitization Bridge:** A dedicated microservice catches "dirty" RTMP streams from Autel drones (fixing metadata errors) and bridges them to standard protocols.
* 🍎 **Apple Silicon Optimized:** Specifically engineered to bypass macOS Docker UDP packet loss issues using native ARM64 images and forced TCP transports.
* 📊 **Full Telemetry Stack:** Integrated MQTT broker, Telegraf agent, and InfluxDB for time-series data storage.
* 💻 **Web Dashboard Ready:** Outputs WebRTC and LL-HLS feeds for easy integration into browser-based frontends.

## 🏗️ System Architecture

The v0.9.1 architecture utilizes a microservices approach to ensure stability. Video responsibilities are split into three distinct containers to prevent failure in one protocol from affecting the other.


### Visual Overview
*(Click the diagram below to enlarge)*

[![v0.9.1 Dual-Lane Architecture](docs/Decision%20Path%20Selection%20Flow-2025-12-14-132635.png)](docs/Decision%20Path%20Selection%20Flow-2025-12-14-132635.png)

## 📡 Connection Lanes & Usage

> **Important:** Replace `<YOUR_IP>` with the actual LAN IP address of your host machine (e.g., `192.168.1.50`). Do **not** use `localhost` on the drone controller.

**Technical Deep Dive:** Read **[docs/VIDEO_PROTOCOLS.md](docs/VIDEO_PROTOCOLS.md)** to understand the differencies between video protocols that Autel supports.

### Lane 1: RTSP (Fast Lane - Low Latency)
Connects directly to the main media server via TCP. Best for real-time piloting cues.
* **Drone Controller Input:** `rtsp://<YOUR_IP>:8554/live/rtsp-drone1`
* **VLC / Player Output:** `rtsp://<YOUR_IP>:8554/live/rtsp-drone1`

### Lane 2: RTMP (Stable Lane - Sanitized)
Ingested by NGINX, cleaned by the FFmpeg bridge, and delivered by the main server. Best for unreliable connections.
* **Drone Controller Input:** `rtmp://<YOUR_IP>:1935/live/rtmp-drone1`
* **VLC / Player Output (Cleaned):** `rtmp://<YOUR_IP>:1936/live/rtmp-drone1`

### 💻 Web Dashboard Outputs
Both lanes are instantly available for browser playback.
* **WebRTC Feed (Lowest Latency):** `http://<YOUR_IP>:8889/live/rtsp-drone1` (or `rtmp-drone1`)
* **LL-HLS Feed:** `http://<YOUR_IP>:8888/live/rtsp-drone1`


### 💻 Mission Control Dashboard
The system outputs a unified "Glass Cockpit" interface, combining low-latency video with real-time tactical mapping.

![Mission Control Dashboard](docs/mission_control_dashboard.png)

* **Left Panel (Visual):**
    * **Source:** `autel_rtsp` container.
    * **Tech:** WebRTC (Port 8889) for <500ms latency.
    * **Config:** `GF_PANELS_DISABLE_SANITIZE_HTML=true` allows direct video embedding.

* **Right Panel (Tactical):**
    * **Source:** `autel_influx` container (via MQTT/Telegraf).
    * **Tech:** Grafana Geomap with Dual Layers (Route Line + Drone Icon).
    * **Data:** Visualizes real-time GPS telemetry (`lat`/`lon`) filtered to remove null island errors.

**Access Feeds Directly:**
* **WebRTC Feed:** `http://<YOUR_IP>:8889/live/rtsp-drone1`
* **HLS Feed:** `http://<YOUR_IP>:8888/live/rtsp-drone1`
   

### 📂 Repository Structure

```text
.
├── config/                  # Service configurations
│   ├── mediamtx.yml         # MediaMTX rules (TCP locking, paths)
│   ├── mosquitto.conf       # MQTT broker settings
│   └── telegraf.conf        # Telegraf data collector config
├── docker/
│   └── docker-compose.yml   # The V0.9.1 Microservices Stack
├── docs/                    # Architecture diagrams & protocol notes
├── scripts/                 # Management utilities (Reset DB, Monitor)
├── src/
│   └── dashboards/          # Frontend resources
│       ├── autel_telemetry_master.json  # Grafana Dashboard (Importable)
│       └── video_panel.html             # Standalone WebRTC Viewer
├── LICENSE
├── README.md                # This file
└── RELEASENOTES.md          # Version history and changelog
```

## 🛠️ Quick Start Deployment

1.  **Prerequisites:** Ensure Docker and Docker Compose are installed.

2.  **Configure Environment:** Create a `.env` file in the root directory with your credentials:
    ```bash
    MQTT_PORT=1883
    GRAFANA_USER=admin
    GRAFANA_PASS=your_secure_password
    INFLUX_USER=admin
    INFLUX_PASS=your_secure_influx_password
    INFLUX_ORG=autel
    INFLUX_BUCKET=telemetry
    INFLUX_TOKEN=your_generated_influx_token
    ```

3.  **Launch the Stack:**
    ```bash
    docker compose --env-file .env -f docker/docker-compose.yml up -d
    ```

4.  **Verify Connectivity:** Access Grafana at `http://localhost:3000` and check container status with `docker ps`.
