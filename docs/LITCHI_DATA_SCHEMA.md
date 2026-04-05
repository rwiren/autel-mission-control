# Litchi Telemetry Data Schema (v1.0 - Deep Dive)

**Source:** Litchi Flight Log CSV Export (`*.csv`)  
**Extraction Date:** 2026-04-05  
**Reference:** Litchi Flight Log Field Reference — [https://flylitchi.com/help#logs](https://flylitchi.com/help#logs)  
**Compatible Models:** All DJI drones supported by the Litchi app (iOS & Android)

This document catalogs the full set of telemetry columns in a Litchi CSV flight log export, as ingested into the InfluxDB `drone_telemetry` measurement via the Telegraf `file` input plugin.

> **Note:** Unlike Autel's push-model MQTT stream, Litchi telemetry is **post-flight**. Log files are pulled from the Litchi Flight Hub API or exported directly from the app after landing. The ingestion pipeline reads CSV rows and writes them as time-series points using the `datetime(utc)` column as the timestamp.

---

## 🕐 1. Timestamp

| Column | Type | Description |
| :--- | :--- | :--- |
| `datetime(utc)` | ISO 8601 String | UTC timestamp of this telemetry sample (`YYYY-MM-DD HH:mm:ss`). Used as the InfluxDB point timestamp. |
| `time(millisecond)` | Int | Milliseconds since flight start. Useful for computing relative timelines. |

---

## 🛰️ 2. Position & Altitude

*GPS-sourced position. Litchi relies on the DJI SDK GNSS subsystem; no RTK support.*

| Column | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `latitude` | Float | ° | Aircraft latitude (WGS-84). |
| `longitude` | Float | ° | Aircraft longitude (WGS-84). |
| `altitude(ft)` | Float | ft | Altitude above takeoff point (imperial). |
| `altitude(m)` | Float | m | Altitude above takeoff point (metric). |
| `ascent(ft)` | Float | ft | Cumulative ascent since takeoff (imperial). |
| `ascent(m)` | Float | m | Cumulative ascent since takeoff (metric). |
| `distance(ft)` | Float | ft | 2D distance from Home Point (imperial). |
| `distance(m)` | Float | m | 2D distance from Home Point (metric). |

---

## ✈️ 3. Speed & Flight Dynamics

*Velocity and attitude data derived from the DJI flight controller.*

| Column | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `speed(mph)` | Float | mph | Ground speed (imperial). |
| `speed(kmh)` | Float | km/h | Ground speed (metric). |
| `speed(m/s)` | Float | m/s | Ground speed (SI). **Recommended for InfluxDB ingestion.** |
| `pitch(deg)` | Float | ° | Nose Up/Down angle. Positive = nose up. |
| `roll(deg)` | Float | ° | Left/Right bank angle. Positive = right roll. |
| `yaw(deg)` | Float | ° | Aircraft heading (0–360°, True North). |
| `directionOfTravel(deg)` | Float | ° | Actual ground track bearing (may differ from yaw in crosswind). |

---

## 🔋 4. Battery & Power

*SoC and voltage sampled at each telemetry interval.*

| Column | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `battery_percent` | Int | % | Remaining State of Charge. |
| `voltage(V)` | Float | V | Total pack voltage at sample time. |

---

## 📡 5. Link Quality & RC Signal

*Radio link and controller health indicators.*

| Column | Type | Range | Description |
| :--- | :--- | :--- | :--- |
| `txrx_signal%` | Int | 0-100 | Bidirectional OcuSync/Lightbridge signal strength. |
| `rc_signal%` | Int | 0-100 | Remote controller link strength specifically. |
| `satellites` | Int | — | Number of GPS satellites locked at sample time. |

---

## 📷 6. Gimbal & Camera Events

*Gimbal orientation and in-flight capture events.*

| Column | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `gimbal_heading(deg)` | Float | ° | Gimbal pan/yaw heading (absolute, 0–360°). |
| `gimbal_pitch(deg)` | Float | ° | Camera tilt angle (-90=Nadir, 0=Forward). |
| `isPhoto` | Bool | — | **1** if a photo was captured at this sample. |
| `isVideo` | Bool | — | **1** if video recording was active at this sample. |

---

## 🗺️ 7. Mission & Waypoint Execution

*State markers emitted during Litchi waypoint mission flights.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `flightPhase` | Enum | Active phase: `"Manual"`, `"Waypoint"`, `"Follow Me"`, `"Orbit"`, `"Track"`. |
| `message` | String | Free-text event log entry (e.g., `"Low Battery"`, `"Takeoff"`, `"Landing"`, waypoint index). |
| `alert_code` | Int | DJI SDK alert/warning code (0 = no alert). Consult DJI SDK docs for code definitions. |

---

## 🛡️ 8. Environmental & Computed Fields

*Derived or environmental fields appended during Telegraf ingestion.*

| Field | Source | Description |
| :--- | :--- | :--- |
| `home_distance_m` | Computed | Equivalent to `distance(m)` — standardized field name for cross-platform dashboard queries. |
| `ground_speed_ms` | Computed | Equivalent to `speed(m/s)` — standardized field name. |
| `flight_id` | Tag | Filename or Flight Hub session ID, used to group all rows from a single flight log. |
| `platform` | Tag | Always `"litchi"` — used to filter in multi-platform Grafana dashboards. |

---

## 📁 Ingestion Pipeline Notes

### CSV → InfluxDB via Telegraf

Add the following to your `telegraf.conf` to ingest Litchi CSV exports:

```toml
[[inputs.file]]
  files = ["/recordings/litchi/*.csv"]
  data_format = "csv"
  csv_header_row_count = 1
  csv_timestamp_column = "datetime(utc)"
  csv_timestamp_format = "2006-01-02 15:04:05"
  csv_tag_columns = ["flight_id"]
  name_override = "drone_telemetry"
```

---

## 📚 References

* **Litchi Flight Log Reference:** [https://flylitchi.com/help#logs](https://flylitchi.com/help#logs)
* **Litchi Flight Hub (Cloud Sync):** [https://flylitchi.com/hub](https://flylitchi.com/hub)
* **DJI SDK Alert Codes:** [DJI Mobile SDK Docs](https://developer.dji.com/mobile-sdk/documentation/)
* **Autel Equivalent:** [DATA_SCHEMA.md](DATA_SCHEMA.md)
* **DJI Equivalent:** [DJI_DATA_SCHEMA.md](DJI_DATA_SCHEMA.md)
* **Dronelink Equivalent:** [DRONELINK_DATA_SCHEMA.md](DRONELINK_DATA_SCHEMA.md)
