# Release Notes

## v1.1.0 - "DJI Parity Release" (2026-04-05)
**Status:** Stable  
**Architect:** RW

### 🚀 Summary
Extends the platform with a full suite of DJI Cloud API operational scripts,
mirroring the existing Autel toolset. All scripts are versioned, fully
commented, and follow the same conventions as their Autel counterparts.

### ✨ New Features
* **`scripts/dji/` — Complete DJI Script Suite:**
  * `flight_recorder.py` (v1.0.0) — MQTT → JSONL log recorder for DJI Cloud API
  * `monitor_mqtt.py` (v1.0.0) — Live packet inspector with colour output
  * `capture_mqtt_schema.py` (v1.0.0) — Deep-merge schema sniffer, writes `docs/dji_raw_schema.json`
  * `inspect_telemetry.py` (v1.0.0) — InfluxDB RTK vs barometric altitude auditor
  * `replay_mission.py` (v1.0.0) — Mission replay for dashboard testing (with bad-packet validation)
  * `generate_schema_report.py` (v1.0.0) — InfluxDB field-key report generator
  * `manage_infra.sh` (v1.0.0) — Docker stack manager with MQTT health check
  * `reset_db.sh` (v1.0.0) — Confirmed-destructive InfluxDB bucket reset

### 🔧 Improvements
* **`scripts/flight_recorder.py`** (Autel) — bumped to v1.1.0; added full docstring,
  `on_connect` callback, explicit `MQTTv311` protocol, and `errors='replace'` decode guard.
* **`scripts/replay_mission.py`** (Autel) — bumped to v1.1.0; added full docstring and
  environment-variable-driven token support.
* **README.md** — updated to reflect DJI support, v1.1.0 badge, new repo structure
  diagram, and an Operational Scripts reference table.
* **DJI scripts** read the InfluxDB token from the `INFLUX_TOKEN` environment variable
  instead of hardcoding it, reducing accidental secret exposure.

---

## v1.0.0 - "The Field Hardened Release" (2025-12-18)
**Status:** Stable Production Release  
**Architect:** RW

### 🚀 Milestone Summary
This release marks the transition from "Engineering Prototype" to **Stable Field System**. The platform has been successfully validated in real-world highway flight tests, demonstrating sub-second video latency and precise telemetry tracking (RTK FIX) over ZeroTier.

### ✨ New Features
* **Live Dashboard Integration:** Added `live_dashboard.png` proving simultaneous Video + Telemetry synchronization.
* **RTK Precision Logic:** Updated `bridge.py` (v1.2.0) to correctly interpret Autel RTK states:
    * `1` = FLOAT (Medium Accuracy)
    * `2` = FIX (Centimeter Accuracy)
* **Dual-Lane Video Config:** Finalized support for both RTSP (Port 8554) and RTMP (Port 1935) ingest pipelines.
* **Persistent Infrastructure:** Docker Compose volumes now strictly mapped to local host folders to prevent data loss on restarts.

### 🐛 Bug Fixes
* **Grafana Login Loop:** Resolved issue where container recreations reset admin passwords; reverted to `.env` file source of truth.
* **Zombie Containers:** Fixed naming conflict between `autel_media` and `autel_rtsp` that caused port binding errors.
* **Choppy Video:** Documented "Standard/720p" bitrate requirement for smooth ZeroTier transmission.

### 📦 Artifacts
* **Golden Dashboard:** `docs/autel_dashboard_v3.json`
* **Bridge Script:** `src/bridge.py` (v1.2.0)


## [v0.9.8] - 2025-12-16 ("The Push Update")
**Status:** Stable / Beta

### 💥 Major Architectural Shift: Push vs Pull
* **Changed:** Switched from a "Pull-based" recorder to a "Push-based" architecture. The Autel Drone now initiates the RTSP connection to the server.
* **Reason:** Solves "Connection Refused" and "404 Not Found" errors caused by ZeroTier NAT traversal and LTE carrier blocking.

### 🚀 New Features
* **Crash-Proof Recording:** Implemented `frag_keyframe+empty_moov` flags. Video files are now playable even if the container crashes or power is lost mid-recording.
* **Auto-Segmentation:** Recordings are automatically split every 15 minutes (`-segment_time 900`) to contain file size and risk.
* **Unified Stack:** Merged `rtsp`, `recorder`, `mqtt`, `influx`, and `grafana` into a single `docker-compose.yml` file for atomic deployments.
* **Jitter Buffer:** Added a 10-second network buffer (`-max_delay 10000000`) to smooth out ZeroTier latency spikes.

### 🐛 Bug Fixes
* **Fixed:** "4-second file loop" caused by FFmpeg panicking on out-of-order packets.
* **Fixed:** Grafana "Failed to Fetch" error by routing video through MediaMTX HLS (Port 8888) instead of raw RTSP.
* **Fixed:** Docker "Invalid Command String" syntax error by converting FFmpeg commands to YAML Arrays.

---

## [v0.9.5] - 2025-12-15 "The Infinity Link"
### 🚀 Major Connectivity Upgrade: ZeroTier SD-WAN
* **Architecture Shift:** Replaced fragile local IP addressing with a **Global Virtual LAN (SD-WAN)**.
* **The "Virtual Cable":** Established a permanent, encrypted tunnel between the Autel Smart Controller V3 and the Mission Control Server (MacBook Pro M4 Max).
* **Key Benefits:**
    * **Static IPs Everywhere:** The Controller is always `...12` and the Server is always `...34`, regardless of 4G/5G/Wi-Fi changes.
    * **NAT Traversal:** ZeroTier punches through mobile carrier NATs automatically—no port forwarding or public IPs required.
    * **Security:** All video and telemetry traffic is end-to-end encrypted.
    * **Ease of Install:** Verified simple APK sideloading on the Controller without rooting.

### 🛠️ Improvements
* **Engineering Dashboard (v2):** Added "Altitude Truth" (Baro vs. RTK) and "Signal Strength" (SDR) gauges.
* **DevOps:** Added `scripts/monitor_video_handshake.sh` for instant connection verification.
* **Docs:** Added `docs/zerotier_path_flow.png` to visualize the new topology.

### 📦 New Artifacts
* `src/dashboards/autel_engineering_v2.json`
* `docs/zerotier_path_flow.png`

---

## v0.9.1 (2025-12-14) - The Dual-Lane Update

### 🌟 Major Features
* **Microservices Video Architecture:** Split video handling into three dedicated containers (`rtsp_server`, `rtmp_server`, `rtmp_bridge`) to ensure isolation and stability.
* **Apple Silicon Native:** Migrated FFmpeg bridge to `mwader/static-ffmpeg` to fix emulation crashes on M1/M2/M3/M4/M5 chips.
* **RTSP TCP Lock:** Enforced `protocols: [tcp]` in MediaMTX to bypass Mac Docker's inability to route UDP video packets.
* **RTMP Sanitizer:** Introduced NGINX ingestion layer to strip "Unsupported Object Type 4" errors from Autel drone streams before they reach the main server.

### 🐛 Bug Fixes
* Fixed "Session Timed Out" (Black Screen) on RTSP connections.
* Fixed "Unsupported Object Type 4" crashes on RTMP connections.
* Fixed `exec format error` in the bridge container on ARM64 architecture.

### ⚠️ Breaking Changes
* **Port Mapping:** * RTSP uses `8554` (Standard).
    * RTMP Ingest uses `1935` (NGINX).
    * RTMP Playback (Cleaned) uses `1936` (MediaMTX).
