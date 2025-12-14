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

```mermaid
flowchart TD
    %% -------------------
    %% NODES: External Hardware
    %% -------------------
    Drone([🚁 Autel Drone])
    Controller([🎮 Controller])
    Browser([💻 Dashboard / Browser])
    VLC([📽️ VLC Player])

    %% -------------------
    %% SUBGRAPH: Docker Microservices Stack (v0.9.1)
    %% -------------------
    subgraph Docker_Host ["🐳 Docker Host (Mac/Linux)"]
        style Docker_Host fill:#e1f5fe,stroke:#01579b,stroke-width:2px
        
        %% Service 1: The Distributor
        subgraph S_RTSP ["📦 autel_rtsp (MediaMTX)"]
            style S_RTSP fill:#d1c4e9,stroke:#512da8
            MTX_Core[Media Server Core]
        end

        %% Service 2: The Sanitizer
        subgraph S_RTMP ["🛡️ autel_rtmp (NGINX)"]
            style S_RTMP fill:#ffccbc,stroke:#bf360c
            NGINX_Ingest[RTMP Ingest]
        end

        %% Service 3: The Worker
        subgraph S_Bridge ["🌉 autel_bridge (FFmpeg)"]
            style S_Bridge fill:#c8e6c9,stroke:#2e7d32
            Bridge_Worker[Stream Copier]
        end
    end

    %% -------------------
    %% LAN### Mermaid Diagram Code
<details>
  <summaE 1: RTSP (Fast Lane)
    %% -------------------
    Drone --"RTSP (TCP) :8554"--> MTX_Core
    %% Note: Direct connection, low latency

    %% -------------------
    %% LANE 2: RTMP (Stable Lane)
    %% -------------------
    Drone --"RTMP (Dirty) :1935"--> NGINX_Ingest
    NGINX_Ingest --"Internal Stream"--> Bridge_Worker
    Bridge_Worker --"RTMP (Cleaned) :1935"--> MTX_Core
    %% Note: Sanitized via Bridge

    %% -------------------
    %% CONSUMERS (Outputs)
    %% -------------------
    MTX_Core --"WebRTC :8889"--> Browser
    MTX_Core --"HLS :8888"--> Browser
    MTX_Core --"RTSP :8554"--> VLC
    
    %% -------------------
    %% CONTROLLER FEEDBACK
    %% -------------------
    %% FIXED LINE BELOW: Label is now correctly inside the dotted link
    Controller -. "Telemetry / Control" .- Drone
```

### Visual Overview
*(Click the diagram below to enlarge)*

[![v0.9.1 Dual-Lane Architecture](docs/Decision%20Path%20Selection%20Flow-2025-12-14-132635.png)](docs/Decision%20Path%20Selection%20Flow-2025-12-14-132635.png)

## 📡 Connection Lanes & Usage

> **Important:** Replace `<YOUR_IP>` with the actual LAN IP address of your host machine (e.g., `192.168.1.50`). Do **not** use `localhost` on the drone controller.

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
