# Release Notes

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
