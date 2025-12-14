# Release Notes

## v0.9.1 (2025-12-14) - The Dual-Lane Update

### 🌟 Major Features
* **Microservices Video Architecture:** Split video handling into three dedicated containers (`rtsp_server`, `rtmp_server`, `rtmp_bridge`) to ensure isolation and stability.
* **Apple Silicon Native:** Migrated FFmpeg bridge to `mwader/static-ffmpeg` to fix emulation crashes on M1/M2/M3 chips.
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
