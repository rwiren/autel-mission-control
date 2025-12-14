# 📊 Autel Telemetry Data Schema

**Version:** v1.0 (Derived from Live Flight Data)
**Measurement Name:** `mqtt_consumer`
**Protocol:** MQTT JSON (Flattened by Telegraf)

---

## 1. Navigation & Positioning (Standard)
*Primary flight data used for general mapping and piloting.*

| Field Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `data_latitude` | Float | Deg | Standard GPS Latitude (WGS84). **Subject to 'Null Island' (0.0) glitches.** |
| `data_longitude` | Float | Deg | Standard GPS Longitude (WGS84). **Subject to 'Null Island' (0.0) glitches.** |
| `data_height` | Float | Meters | Barometric/GPS fused altitude (AMSL or Relative to Takeoff). |
| `data_horizontal_speed` | Float | m/s | Ground speed. |
| `data_vertical_speed` | Float | m/s | Climb/Descent rate. |
| `data_attitude_head` | Float | Deg | Drone Heading (Yaw). |
| `data_attitude_pitch` | Float | Deg | Drone Pitch. |
| `data_attitude_roll` | Float | Deg | Drone Roll. |
| `data_position_state_gps_number` | Float | Count | Number of satellites locked (Standard GNSS). |

---

## 2. RTK Precision Data (Real-Time Kinematic)
*Used for centimeter-level accuracy. Compare these against Standard fields to determine deviation.*

| Field Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `data_position_state_rtk_lat` | Float | Deg | RTK-corrected Latitude. |
| `data_position_state_rtk_lon` | Float | Deg | RTK-corrected Longitude. |
| `data_position_state_rtk_hgt` | Float | Meters | RTK Ellipsoidal Height (Very precise). |
| `data_position_state_rtk_number` | Float | Count | Number of RTK satellites/signals used (e.g., 20+). |
| `data_position_state_rtk_used` | Float | Bool | `1.0` = RTK in use, `0.0` = Standard GPS only. |
| `data_position_state_is_fixed` | Float | Enum | `3.0` usually indicates "Fixed" (High Precision). |

---

## 3. Altitude & Environment Analysis
*Critical for "True Height" determination.*

| Field Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `data_height` | Float | m | Standard fused height. |
| `data_position_state_rtk_hgt` | Float | m | RTK Geometry height. |
| `data_ned_altitude` | Float | m | North-East-Down coordinate Z-axis (often local frame). |
| `data_elevation` | Float | m | Terrain elevation (if available in map data) or relative. |
| `data_height_limit` | Float | m | Max ceiling set in controller (e.g., 120.0). |
| `data_home_distance` | Float | m | Distance from Home Point. |

---

## 4. Power & Battery System
| Field Name | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `data_battery_capacity_percent` | Float | % | Main battery charge. |
| `data_battery_voltage` | Float | mV | Real-time voltage (e.g., 15839.0 = 15.8V). |
| `data_battery_remain_flight_time` | Float | Sec | Estimated time remaining (e.g., 1890). |
| `data_battery_landing_power` | Float | Watts? | Power reserve threshold for landing. |

---

## 5. Gimbal & Camera
| Field Name | Type | Description |
| :--- | :--- | :--- |
| `data_10052-0-0_gimbal_pitch` | Float | Camera Pitch Angle (e.g., -90 for looking down). |
| `data_10052-0-0_gimbal_yaw` | Float | Camera Yaw Angle. |
| `data_10052-0-0_zoom_factor` | Float | Digital/Optical Zoom Level (e.g., 1.56). |
| `data_cameras_0_recording_state` | Float | `1.0` = Recording, `0.0` = Idle. |

---

## 🔬 Data Science: Comparative Queries

### A. RTK vs. Standard GPS Accuracy
Use this Flux query to plot the "Drift" between the cheap GPS and the expensive RTK:

```flux
from(bucket: "telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "data_latitude" or r["_field"] == "data_position_state_rtk_lat")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> map(fn: (r) => ({
      _time: r._time,
      lat_diff: r.data_latitude - r.data_position_state_rtk_lat
  }))
