# Autel Mission Control

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Docker%20%7C%20Mac%20Silicon-lightgrey.svg)]()
![Last Updated](https://img.shields.io/github/last-commit/rwiren/autel-mission-control?label=Last%20Updated&color=orange)

> **A centralized mission control hub for Autel drones, delivering specialized dual-lane real-time video streaming and comprehensive telemetry logging via Docker.**

---

### 📢 🆕 Latest Updates: v0.9.8 released!
**[Click here to view the RELEASENOTES.md for detailed changelogs and architecture shifts.](RELEASENOTES.md)**

---

## 📖 Table of Contents
1.  [Project Overview](#-project-overview)
2.  [Key Features](#-key-features)
3.  [System Architecture (Evolution)](#-system-architecture)
4.  [Connectivity & Drone Config](#-connectivity--usage)
5.  [Dashboards](#-mission-control--engineering-dashboards)
6.  [Quick Start Deployment](#-quick-start-deployment)
7.  [References](#-references--research)

---

## 🔭 Project Overview

**Autel Mission Control** is a field server designed for enterprise drone operations. It solves the critical challenge of reliable video recording over high-latency networks (ZeroTier/LTE/4G) by inverting the standard connection model.

Instead of the server "pulling" video (which often fails behind NATs/VPNs), the Drone Controller **pushes** the stream to this node. The system then captures, segments, and indexes the footage using industrial-grade fault tolerance, ensuring that even if power is lost, the mission data is saved.

## 🚀 Key Features

* 🎥 **Active "Push" DVR:** Drone initiates the connection, pushing RTSP directly to the local MediaMTX server (TCP Port 8554).
* 🛡️ **Crash-Resilient Recording:** Uses **Fragmented MP4 (fMP4)** storage. If the container crashes or power is cut, the video file is saved up to the last second (solving the "Moov Paradox").
* 🛡️ **Network Jitter Buffer:** A 10-second buffer smooths out latency spikes common on LTE/5G/ZeroTier connections, preventing recording gaps.
* 📊 **Unified Telemetry Stack:** Integrated MQTT broker, Telegraf agent, InfluxDB, and Grafana for visualizing drone data.
* 🍎 **Apple Silicon Native:** Optimized for macOS ARM64 architecture with `host` networking mode for seamless ZeroTier integration.
* 🕸️ **Web Dashboard Ready:** Automatically transmuxes RTSP feeds to **HLS (Port 8888)** for native browser playback in Grafana.

---

## 🏗️ System Architecture

The v0.9.1 architecture utilized a microservices approach to ensure stability. Video responsibilities are split into three distinct containers to prevent failure in one protocol from affecting the other.

---

### Visual Overview
*(Click the diagram below to enlarge)*

[![v0.9.1 Dual-Lane Architecture](docs/Decision%20Path%20Selection%20Flow-2025-12-14-132635.png)](docs/Decision%20Path%20Selection%20Flow-2025-12-14-132635.png)


The v0.9.8 architecture unifies the video and telemetry pipelines into a single, atomic Docker stack, replacing the previous microservices web.

### Visual Overview
*(Click the diagram below to enlarge)*


[![v0.9.8 Push Architecture](docs/architecture_v3.png)](docs/architecture_v3.png)

### The Pipeline
1.  **Ingest (The "Push"):** `bluenviron/mediamtx` (TCP Port 8554) acts as the passive receiver for the Drone's RTSP connection.
2.  **Archival (The "Engine"):** `linuxserver/ffmpeg` pulls the stream locally, applies wallclock timestamps, and writes crash-proof **15-minute segments**.
3.  **Visualization (The "View"):** `grafana/grafana` pulls telemetry from InfluxDB and renders the live video via **HLS** (Port 8888).

---

## 📡 Connectivity & Usage

> **Critical:** This system operates on a **Push Model**. You must configure the Drone to send data to the server; the server will not "find" the drone automatically.

### 1. The ZeroTier "Virtual Cable"
Unlike standard setups that break when you switch networks, this project uses **ZeroTier** to create a static, encrypted tunnel.

![ZeroTier Data Flow](docs/zerotier_path_flow.png)

### 2. Drone Configuration (The "Push")
Configure the **Autel Enterprise App** (Live Stream settings) to push to these endpoints:

* **Video (RTSP):** `rtsp://<SERVER_ZT_IP>:8554/live/rtsp-drone1`
* **Telemetry (MQTT):** `<SERVER_ZT_IP>` (Port 1883)

### 3. Mission Control Outputs (The "View")
* **Web Dashboard (HLS):** `http://<SERVER_ZT_IP>:8888/live/rtsp-drone1/index.m3u8` (Best for Grafana/Browser)
* **Low-Latency (RTSP):** `rtsp://<SERVER_ZT_IP>:8554/live/rtsp-drone1` (Best for VLC)

---

## 💻 Mission Control & Engineering Dashboards
The system includes a "Golden Image" Grafana dashboard (**[docs/autel_dashboard_v3.json](docs/autel_dashboard_v3.json)**) that unifies real-time video, tactical mapping, and hardware diagnostics.

### 1. The Tactical View
*Combines live video (HLS) with a geospatial map for situational awareness.*

![Mission Control Dashboard](docs/archive/mission-control-dashboard.png)

### 2. The Engineering View (Hardware Forensics)
*Exposes raw sensor comparisons to detect hardware drift.*

![Engineering Dashboard](docs/archive/autel_dashboard2.png)

* **🛰️ Precision Lock:** Visualizes GNSS vs. RTK satellite count delta (Goal: 50+ sats).
* **⛰️ Altitude Truth:** Plots Barometric vs. Ellipsoidal height to detect pressure drift.
* **🔋 Battery Profiling:** Monitors voltage sag under throttle load.
---  

### 📂 Repository Structure

```text
.
├── config/                  # Service configurations (MediaMTX, Telegraf)
├── docker/
│   └── docker-compose.yml   # The Unified v0.9.8 Stack
├── docs/                    # Architecture (v3), Golden Dashboards, & Research
│   ├── archive/             # Deprecated diagrams and v2 layouts
│   ├── architecture_v3.png  # Current System Flow
│   └── autel_dashboard_v3.json # Production Grafana Dashboard
├── recordings/              # Auto-segmented video files (15-min chunks)
├── scripts/                 # Operational utilities (Infra management, Monitors)
├── src/                     # Python helper modules & Legacy dashboards
├── LICENSE
├── README.md                # This file
├── RELEASENOTES.md          # Version history
└── .env.example             # Template for secrets
```

---

## 🌐 Connectivity: The ZeroTier "Virtual Cable"

Unlike standard setups that break when you switch from Home Wi-Fi to a Field Hotspot, this project uses **ZeroTier** to create a permanent, encrypted virtual LAN.

### The Architecture
![ZeroTier Data Flow](docs/zerotier_path_flow.png)

This topology allows the **Field Unit** (Drone + Controller) and **Mission Control** (Server) to behave as if they are plugged into the same physical switch, even when miles apart on different 4G/5G networks.

### ⚡ Why We Use ZeroTier?
1.  **Static IPs Forever:**
    * The Controller is assigned `192.168.x.12`.
    * The Server is assigned `192.168.x.34`.
    * *Benefit:* We never have to reconfigure the Drone's RTMP URL when moving locations.
2.  **NAT Traversal (The "Magic"):**
    * Standard mobile hotspots (4G/5G) use CGNAT, which blocks incoming connections.
    * *Benefit:* ZeroTier punches through these barriers automatically. No port forwarding or static public IPs are needed from your ISP.
3.  **End-to-End Encryption:**
    * *Benefit:* Your live video feed and telemetry are encrypted inside the tunnel, protecting them from public internet snooping.
4.  **Simple Installation:**
    * *Benefit:* The Autel Smart Controller V3 runs Android, allowing us to simply sideload the official [ZeroTier APK](http://download.zerotier.com/dist/ZeroTierOne.apk) via the browser. No rooting or complex hacking required.

### 📡 Data Flow Summary
* **Video:** Drone -> Controller -> **ZeroTier Tunnel** -> Server (Port 1935 RTMP and 8554 RTSP)
* **Telemetry:** Drone -> Controller -> **ZeroTier Tunnel** -> Server (Port 1883 MQTT)

---

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

---

## 📚 References & Research

* **Video Resilience Strategy:** [Solving Fragmented RTSP_MP4 Recordings.pdf](docs/Solving%20Fragmented%20RTSP_MP4%20Recordings.pdf) - Internal architecture document detailing the move to fMP4.
* **Video Protocols:** [VIDEO_PROTOCOLS.md](docs/VIDEO_PROTOCOLS.md) - Comparison of RTSP vs RTMP.
* **Autel Cloud API:** [SDK Reference](https://doc.autelrobotics.com/cloud_api/en/60/30/00/10/00) - MQTT topic definitions.
