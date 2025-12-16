# Autel Telemetry Data Schema (v1.0 - Deep Dive)

**Source:** MQTT Topic `thing/product/+/osd`  
**Extraction Date:** 2025-12-16  
**Drone Model:** Autel Evo Max 4T

This document catalogs the full spectrum of telemetry fields available in the InfluxDB `drone_telemetry` measurement.

---

## 🛰️ 1. RTK & High-Precision Positioning
*The "Truth" source for mapping and automated landing.*

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `data_Rtk_rtkStatus` | Int | **50**=Fixed (Safe), **34**=Float (Caution), **16**=Single (Danger) |
| `data_Rtk_posType` | Int | **50**=Narrow Integer (Best), **1**=Omni, **0**=None |
| `data_Rtk_diffStatus` | Int | **1**=Receiving Corrections (Base/NTRIP active) |
| `data_Rtk_satelliteCount` | Int | Satellites used by the RTK algorithm (Rover). |
| `data_Rtk_baseStationCount` | Int | Satellites seen by the Base Station. |
| `data_Rtk_altitude` | Float | Ellipsoidal Height (m). Geometric truth (ignores pressure). |
| `data_Rtk_latitude` | Float | RTK Latitude (8 decimal precision). |
| `data_Rtk_longitude` | Float | RTK Longitude (8 decimal precision). |
| `data_Rtk_hAcc` | Float | Horizontal Accuracy estimate (meters). |
| `data_Rtk_yaw` | Float | Heading derived from dual-antenna RTK (Magnetic immune). |

---

## 🔋 2. Smart Battery System
*Cell-level diagnostics for analyzing voltage sag and health.*

| Field Key | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `data_Battery_voltage` | Int | mV | Total pack voltage (e.g., `16400` = 16.4V). |
| `data_Battery_current` | Int | mA | Instantaneous current draw. Negative = Charging. |
| `data_Battery_capacity` | Int | % | Remaining State of Charge (SoC). |
| `data_Battery_temperature` | Float | °C | Pack core temperature. **>55°C** is critical. |
| `data_Battery_cycleCount` | Int | Count | Total charge cycles (Health indicator). |
| `data_SmartBattery_cell1` | Int | mV | Voltage of Cell 1 (Drift detection). |
| `data_SmartBattery_cell2` | Int | mV | Voltage of Cell 2. |
| `data_SmartBattery_cell3` | Int | mV | Voltage of Cell 3. |
| `data_SmartBattery_cell4` | Int | mV | Voltage of Cell 4. |
| `data_SmartBattery_designCap` | Int | mAh | Factory design capacity. |
| `data_SmartBattery_fullCap` | Int | mAh | Current max capacity (Degradation tracking). |

---

## ✈️ 3. Flight Dynamics & IMU
*Raw sensor data for analyzing stability and wind resistance.*

| Field Key | Unit | Description |
| :--- | :--- | :--- |
| `data_Imu_attiPitch` | Deg | Nose Up/Down angle. |
| `data_Imu_attiRoll` | Deg | Left/Right tilt angle. |
| `data_Imu_attiYaw` | Deg | Heading (Magnetic/True North). |
| `data_Gps_speed_x` | m/s | Velocity East/West. |
| `data_Gps_speed_y` | m/s | Velocity North/South. |
| `data_Gps_speed_z` | m/s | Vertical Velocity (Climb/Sink rate). |
| `data_Drone_gearState` | Enum | **1**=Down, **2**=Up (Retractable landing gear). |
| `data_Drone_flightMode` | Enum | **1**=Manual, **2**=GPS, **3**=ATTI, **6**=Mission. |

---

## 📡 4. Link Quality & Remote Controller
*Predicting signal loss before it happens.*

| Field Key | Range | Description |
| :--- | :--- | :--- |
| `data_Link_signalQuality` | 0-100 | Overall Signal Strength (RSSI equivalent). |
| `data_Link_uplinkQuality` | 0-100 | Controller -> Drone command link health. |
| `data_Link_downlinkQuality` | 0-100 | Drone -> Screen video link health. |
| `data_RC_leftStickX` | -1000..1000 | Pilot Input: Yaw. |
| `data_RC_leftStickY` | -1000..1000 | Pilot Input: Throttle. |
| `data_RC_rightStickX` | -1000..1000 | Pilot Input: Roll. |
| `data_RC_rightStickY` | -1000..1000 | Pilot Input: Pitch. |

---

## 📷 5. Gimbal & Camera
*Payload orientation and state.*

| Field Key | Unit | Description |
| :--- | :--- | :--- |
| `data_Gimbal_pitch` | Deg | Camera tilt (-90=Down, 0=Forward). |
| `data_Gimbal_roll` | Deg | Horizon leveling. |
| `data_Gimbal_yaw` | Deg | Pan angle relative to aircraft nose. |
| `data_Camera_state` | Enum | **1**=Idle, **2**=Recording, **3**=Taking Photo. |
| `data_Camera_sdCardState` | Enum | **0**=Normal, **1**=Full, **2**=Error. |
| `data_Camera_remainTime` | Seconds | Video recording time remaining on SD card. |

---

## 🛡️ 6. Safety Systems (Radar/Avoidance)

| Field Key | Type | Description |
| :--- | :--- | :--- |
| `data_Avoidance_state` | Bool | **1**=Obstacle Avoidance Active. |
| `data_Radar_distance` | Float | Distance to nearest object (mmWave Radar). |
| `data_Drone_homeDist` | Float | Distance from Home Point (2D). |
| `data_Drone_homeHeight` | Float | Height relative to Home Point takeoff. |
