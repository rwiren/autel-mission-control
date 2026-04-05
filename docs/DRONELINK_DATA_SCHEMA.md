# Dronelink Telemetry Data Schema (v1.0 - Deep Dive)

**Source:** Dronelink Mission Execution Engine (Unified State API)  
**Extraction Date:** 2026-04-05  
**Reference:** Dronelink Developer Docs — [https://dronelink.com/docs](https://dronelink.com/docs)  
**Compatible Platforms:** DJI (via Mobile SDK / MSDK v5), Autel (via Autel SDK), Parrot (via Olympe)

This document catalogs the unified telemetry state fields emitted by the Dronelink SDK during connected flight sessions, as stored in the InfluxDB `drone_telemetry` measurement.

> **Note:** Dronelink abstracts over manufacturer-specific SDKs and presents a **normalized** telemetry model. The same field names apply regardless of whether the physical drone is DJI, Autel, or another supported platform. This enables cross-fleet dashboards without schema changes.

---

## 🛰️ 1. Position & Altitude

*Unified positioning fields, sourced from the active drone's GNSS/RTK subsystem.*

| Field Key | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `location.latitude` | Float | ° | Aircraft latitude (WGS-84). |
| `location.longitude` | Float | ° | Aircraft longitude (WGS-84). |
| `location.altitude` | Float | m | Altitude above Mean Sea Level (MSL). |
| `location.altitudeAboveTakeoff` | Float | m | Height above the recorded takeoff point. |
| `homeLocation.latitude` | Float | ° | Home point latitude (set at takeoff or updated during flight). |
| `homeLocation.longitude` | Float | ° | Home point longitude. |
| `distanceToHome` | Float | m | Horizontal distance from the current position to the home point. |

---

## 🔋 2. Battery & Power

*State-of-charge and power metrics normalized across battery types.*

| Field Key | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `battery.charge` | Float | 0.0–1.0 | Normalized State of Charge (1.0 = 100%). |
| `battery.chargePercent` | Int | % | Remaining SoC as an integer percentage. |
| `battery.voltage` | Float | V | Total pack voltage. |
| `battery.current` | Float | A | Instantaneous current draw (positive = discharging). |
| `battery.temperature` | Float | °C | Pack temperature. **>55°C** is a critical warning. |
| `battery.timeRemaining` | Int | s | Estimated seconds of flight remaining based on current draw. |
| `battery.cellCount` | Int | — | Number of cells in the active battery pack. |

---

## ✈️ 3. Orientation & Flight Dynamics

*Normalized attitude and velocity from the IMU and flight controller.*

| Field Key | Unit | Description |
| :--- | :--- | :--- |
| `orientation.x` (pitch) | Rad | Nose Up/Down angle in radians. |
| `orientation.y` (roll) | Rad | Left/Right bank angle in radians. |
| `orientation.z` (yaw) | Rad | Heading (0 = North, values in radians). |
| `velocity.horizontal` | m/s | Ground speed in the horizontal plane. |
| `velocity.vertical` | m/s | Climb/Sink rate (positive = ascending). |
| `velocity.course` | Rad | Ground track bearing (direction of travel). |

---

## 📡 4. Signal & RC Link Quality

*Link health metrics surfaced through the manufacturer SDK.*

| Field Key | Range | Description |
| :--- | :--- | :--- |
| `remoteController.signalQuality` | 0.0–1.0 | Normalized RC signal strength (1.0 = excellent). |
| `downlinkSignalQuality` | 0.0–1.0 | Drone → Controller video/data link health. |
| `uplinkSignalQuality` | 0.0–1.0 | Controller → Drone command link health. |
| `satelliteCount` | Int | Number of GNSS satellites currently acquired. |

---

## 📷 5. Gimbal & Camera

*Payload orientation and recording state, abstracted for all supported payloads.*

| Field Key | Unit | Description |
| :--- | :--- | :--- |
| `gimbal.orientation.x` (pitch) | Rad | Camera tilt (−π/2 = Nadir, 0 = Forward). |
| `gimbal.orientation.y` (roll) | Rad | Horizon-leveling roll compensation. |
| `gimbal.orientation.z` (yaw) | Rad | Pan angle relative to aircraft nose. |
| `camera.isCapturing` | Bool | **true** if a photo capture is in progress. |
| `camera.isRecording` | Bool | **true** if video recording is active. |
| `camera.storageLocation` | Enum | Active storage: **SD** or **Internal**. |
| `camera.remainingStorageSpace` | MB | Free space on the active storage medium. |

---

## 🗺️ 6. Mission & Plan Execution

*Dronelink-specific execution state emitted during automated component execution.*

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `mission.componentIndex` | Int | Index of the active mission component (e.g., map, waypoint, orbit). |
| `mission.estimatedTotalDistance` | Float | Total planned path distance (m). |
| `mission.distanceCompleted` | Float | Distance flown so far within the current mission (m). |
| `mission.estimatedTotalTime` | Float | Planned total mission duration (s). |
| `mission.timeElapsed` | Float | Seconds elapsed since mission start. |
| `mission.engagementState` | Enum | **Disengaged**, **Engaging**, **Engaged**, **Disengaging**. |
| `mission.reengagementCount` | Int | Number of times the mission was paused and resumed (fault indicator). |

---

## 🛡️ 7. Safety & Flight Controller State

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `flightMode` | String | Active flight controller mode string (SDK-native value, e.g., `"GPS"`, `"ATTI"`, `"Waypoint"`). |
| `isFlying` | Bool | **true** if the aircraft is airborne. |
| `isLanding` | Bool | **true** if an auto-landing sequence is active. |
| `isReturningHome` | Bool | **true** if an RTH sequence is active. |
| `obstacleAvoidanceEnabled` | Bool | **true** if the active drone's avoidance system is enabled. |
| `lowBatteryWarning` | Bool | **true** when SoC crosses the configured low-battery threshold. |
| `criticalBatteryWarning` | Bool | **true** when SoC crosses the critical/forced-landing threshold. |

---

## 📚 References

* **Dronelink Developer Documentation:** [https://dronelink.com/docs](https://dronelink.com/docs)
* **Dronelink GitHub (Extensions/SDK):** [https://github.com/dronelink](https://github.com/dronelink)
* **Autel Equivalent:** [DATA_SCHEMA.md](DATA_SCHEMA.md)
* **DJI Equivalent:** [DJI_DATA_SCHEMA.md](DJI_DATA_SCHEMA.md)
