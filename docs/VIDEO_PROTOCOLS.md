# 🎥 Video Streaming Protocols

Autel Mission Control supports multiple streaming standards to balance **latency** vs. **compatibility**.

## 1. RTSP (Real-Time Streaming Protocol)
**The Gold Standard for Drones.**
* **Used By:** Autel Smart Controller, VLC, QGroundControl.
* **Latency:** Ultra-low (200ms - 500ms).
* **Port:** `8554`
* **How it works:** Establishes a direct control channel between the drone and the server. It is preferred over RTMP because it supports UDP transport, which handles packet loss better in flight.

## 2. GB28181 (Public Security Standard)
**The Enterprise Surveillance Standard.**
* **Used By:** Large-scale security grids, Police/Fire command centers (China/Asia specific).
* **Latency:** Medium (500ms - 1s).
* **Feature:** Allows the drone to register itself to a central government or enterprise server automatically.
* **Status in Project:** *Experimental Support via MediaMTX.*

## 3. RTMP (Real-Time Messaging Protocol)
**The Legacy Broadcaster.**
* **Used By:** YouTube Live, Twitch, OBS Studio.
* **Latency:** High (2s - 10s).
* **Port:** `1935`
* **Why avoid it?** It relies on TCP, which causes "buffering" if the signal gets weak. RTSP/UDP just skips the bad frames, keeping the video "live."

## 4. WebRTC
**The Modern Web Standard.**
* **Used By:** Modern Browsers (Chrome/Safari) without plugins.
* **Latency:** < 500ms.
* **Port:** `8889`
* **Usage:** This is what allows us to show the video directly on the Grafana Dashboard.
