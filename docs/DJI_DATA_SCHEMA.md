# DJI Telemetry Data Schema (v1.0 - Deep Dive)

**Source:** MQTT Topic `thing/product/{device_sn}/osd`  
**Extraction Date:** 2026-04-05  
**Reference:** DJI Cloud API — [Official Docs](https://developer.dji.com/doc/cloud-api-tutorial/en/)  
**Compatible Models:** DJI Matrice 30T, Matrice 350 RTK, Mavic 3 Enterprise Series

This document catalogs the telemetry fields published over the DJI Cloud API MQTT broker into the InfluxDB `drone_telemetry` measurement.

> **Note:** DJI's Cloud API uses the same `thing/product/{sn}/osd` topic structure as Autel. The field naming convention differs but the ingestion pipeline is identical.

---

## 🛰️ 1. RTK & High-Precision Positioning

*The "Truth" source for precision mapping and automated landing.*

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `latitude` | Float | Aircraft latitude (WGS-84, 6-decimal precision). |
| `longitude` | Float | Aircraft longitude (WGS-84, 6-decimal precision). |
| `height` | Float | Takeoff-relative altitude (m). |
| `elevation` | Float | Ellipsoidal height above sea level (m). RTK-corrected. |
| `rtk_state` | Int | **0**=Disabled, **1**=Single, **2**=Float, **3**=Fixed. |
| `rtk_yaw` | Float | Heading from dual-antenna RTK (°, True North, magnetic immune). |
| `rtk_yaw_enable` | Bool | **1**=RTK yaw source active. |
| `rtk_position_enable` | Bool | **1**=RTK position source active. |
| `gear` | Int | **1**=Down, **2**=Up (retractable landing gear state). |
| `position_state` | Object | GNSS fix quality: `is_fixed`, satellite counts (`gps_number`, `glonass_number`, `beidou_number`, `galileo_number`). |

---

## 🔋 2. Smart Battery System

*Cell-level diagnostics for analyzing voltage sag, cycle life, and thermal health.*

| Field Key | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `battery.capacity_percent` | Int | % | Remaining State of Charge (SoC). |
| `battery.landing_power` | Int | % | SoC threshold at which forced landing is triggered. |
| `battery.return_home_power` | Int | % | SoC threshold at which auto Return-to-Home is triggered. |
| `battery.remain_flight_time` | Int | s | Estimated flight time remaining. |
| `battery.remain_fly_distance` | Int | m | Estimated flight range remaining. |
| `battery.lowest_voltage` | Int | mV | Lowest cell voltage in the pack (drift detection). |
| `battery.batteries[n].voltage` | Int | mV | Total voltage of battery slot `n`. |
| `battery.batteries[n].temperature` | Float | °C | Core temperature. **>55°C** is critical. |
| `battery.batteries[n].high_voltage_storage_days` | Int | Days | Days stored above 80% SoC (longevity warning). |
| `battery.batteries[n].type` | Int | — | Battery model identifier. |

---

## ✈️ 3. Flight Dynamics & IMU

*Attitude, velocity, and flight-mode state for stability analysis.*

| Field Key | Unit | Description |
| :--- | :--- | :--- |
| `attitude_pitch` | Deg | Nose Up/Down angle. |
| `attitude_roll` | Deg | Left/Right tilt angle. |
| `attitude_yaw` | Deg | Magnetic heading (° from North). |
| `horizontal_speed` | m/s | Ground speed (horizontal plane). |
| `vertical_speed` | m/s | Climb/Sink rate (positive = ascending). |
| `wind_speed` | m/s | Estimated wind speed at current altitude. |
| `wind_direction` | Int | Wind bearing (°, 0-360). |
| `mode_code` | Enum | **0**=Standby, **1**=Takeoff Ready, **2**=Manual, **3**=Auto-Takeoff, **4**=Wayline, **5**=RTH, **6**=Landing, **7**=Forced Landing, **8**=Three-Propeller Emergency. |

---

## 📡 4. Link Quality & Remote Controller

*Signal health indicators for predicting command loss before it occurs.*

| Field Key | Range | Description |
| :--- | :--- | :--- |
| `wireless_link.signal_quality` | 0-100 | Overall RF signal quality (RSSI equivalent). |
| `wireless_link.uplink_quality` | 0-100 | Controller → Drone command link health. |
| `wireless_link.downlink_quality` | 0-100 | Drone → Controller video/data link health. |
| `wireless_link.frequency_band` | Enum | **1**=2.4 GHz, **2**=5.8 GHz, **3**=900 MHz (region-dependent). |
| `wireless_link.channel_noise` | Int | RF channel noise floor (lower is better). |
| `rc_lost_action` | Enum | **0**=Hover, **1**=Landing, **2**=RTH (configured behavior on RC loss). |
| `home_distance` | Float | Distance from Home Point (2D, meters). |

---

## 📷 5. Gimbal & Camera Payload

*Payload orientation and recording state.*

| Field Key | Unit | Description |
| :--- | :--- | :--- |
| `gimbal_pitch` | Deg | Camera tilt (-90=Nadir, 0=Forward). |
| `gimbal_roll` | Deg | Horizon leveling compensation angle. |
| `gimbal_yaw` | Deg | Pan angle relative to aircraft nose. |
| `payload_index` | Enum | Active payload slot (e.g., **0**=Main Camera, **1**=FPV). |
| `cameras[n].photo_state` | Enum | **0**=Idle, **1**=Capturing. |
| `cameras[n].video_state` | Enum | **0**=Idle, **1**=Recording. |
| `cameras[n].storage.used` | MB | Used storage on internal or SD media. |
| `cameras[n].storage.total` | MB | Total storage capacity. |
| `cameras[n].remain_record_duration` | s | Video recording time remaining on current media. |

---

## 🛡️ 6. Safety Systems & Obstacle Avoidance

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `obstacle_avoidance.type` | Enum | **0**=Disabled, **1**=APAS (Active), **2**=Brake Only. |
| `obstacle_avoidance.horizon` | Bool | **1**=Horizontal sensing active. |
| `obstacle_avoidance.upside` | Bool | **1**=Upward sensing active. |
| `obstacle_avoidance.downside` | Bool | **1**=Downward sensing / precision landing active. |
| `night_lights_state` | Bool | **1**=Aircraft navigation lights on. |
| `distance_limit_status.state` | Bool | **1**=Max radius limit enforced. |
| `distance_limit_status.distance_limit` | Float | Configured max flight radius (m) from Home Point. |
| `height_limit` | Float | Maximum altitude cap (m AGL) set in the app. |

---

## 🗺️ 7. Mission & Wayline Execution

*State fields emitted during automated wayline (waypoint) missions.*

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `current_waypoint_index` | Int | Index of the active waypoint in the current mission. |
| `wayline_progress` | Float | Mission completion percentage (0.0–1.0). |
| `current_wayline_id` | String | Identifier of the active wayline task. |
| `track_id` | String | Unique flight session identifier (correlates video with telemetry). |

---

## 📚 References

* **DJI Cloud API MQTT Topics:** [https://developer.dji.com/doc/cloud-api-tutorial/en/](https://developer.dji.com/doc/cloud-api-tutorial/en/)
* **Matrice 350 RTK User Manual:** [DJI Enterprise Docs](https://enterprise.dji.com/matrice-350-rtk)
* **Autel Equivalent:** [DATA_SCHEMA.md](DATA_SCHEMA.md)
