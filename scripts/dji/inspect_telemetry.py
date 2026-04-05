#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: inspect_telemetry.py
Description: Development-grade DJI telemetry inspector for InfluxDB.
             1. Scans data volume (last 4 hours).
             2. Checks sensor health — RTK vs Barometric altitude.
             3. "Action Finder": locates takeoff/landing by detecting motion.
             4. Calculates geoid offset (altitude truth analysis).

             Mirrors the Autel inspect_telemetry.py but targets the DJI
             Cloud API field names (see docs/DJI_DATA_SCHEMA.md).
Version:     1.0.0
Author:      RW
Date:        2026-04-05
-----------------------------------------------------------------------------
Usage:
    python3 inspect_telemetry.py

    Requires InfluxDB to be running and populated by the DJI telemetry
    bridge (or the Telegraf MQTT consumer).

Dependencies:
    pip install influxdb-client
-----------------------------------------------------------------------------
"""

import statistics
from influxdb_client import InfluxDBClient

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
INFLUX_URL    = "http://localhost:8086"
INFLUX_ORG    = "dji_ops"
INFLUX_BUCKET = "drone_telemetry"

# Read token from environment variable for security; fall back to placeholder.
# Set: export INFLUX_TOKEN="your-token-here"
import os
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-super-secret-token-change-me")

# Analysis window — look back this far for a flight session
TIME_RANGE = "-4h"

# Geoid offset: DJI `elevation` (ellipsoidal) is typically higher than
# `height` (takeoff-relative AGL). Calibrate from your first flight.
# A value of 0.0 means "no correction applied yet".
GEOID_OFFSET = 0.0

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def print_header(text: str):
    print(f"\n{'=' * 60}")
    print(f" {text}")
    print(f"{'=' * 60}")

# ---------------------------------------------------------------------------
# MAIN ANALYSIS
# ---------------------------------------------------------------------------

def inspect_bucket():
    print_header(f"📡 DJI TELEMETRY INSPECTOR v1.0.0 | Window: {TIME_RANGE}")

    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
        timeout=60_000
    )
    query_api = client.query_api()

    try:
        # ---------------------------------------------------------------
        # PART 1: General Volume Scan
        # ---------------------------------------------------------------
        print("🔍 Step 1: Scanning data volume...")

        stats_query = f"""
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: {TIME_RANGE})
          |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
          |> count()
          |> group(columns: ["_field"])
          |> sum()
        """

        result      = query_api.query(stats_query)
        field_counts = {}

        for table in result:
            for record in table:
                field = record.get_field()
                count = record.get_value()
                if field and count:
                    field_counts[field] = count

        if not field_counts:
            print(f"   ⚠️  No data found in the last {TIME_RANGE}.")
            print("   Ensure the DJI bridge/Telegraf is running and the drone is powered on.")
            return

        print(f"   ✅ Data found! Active fields: {len(field_counts)}")

        # ---------------------------------------------------------------
        # PART 2: Action Finder (Takeoff / Landing Detection)
        # ---------------------------------------------------------------
        print_header("🎬 Step 2: Locating High-Motion Segment (Takeoff/Landing)")
        print(f"   Applying geoid offset of -{GEOID_OFFSET:.2f}m to RTK elevation data...")

        # DJI field names (from docs/DJI_DATA_SCHEMA.md):
        #   elevation — ellipsoidal height (RTK, sea-level reference)
        #   height    — takeoff-relative AGL altitude (barometric)
        accuracy_query = f"""
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: {TIME_RANGE})
          |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
          |> filter(fn: (r) => r["_field"] == "elevation" or r["_field"] == "height")
          |> aggregateWindow(every: 1s, fn: mean, createEmpty: true)
          |> fill(usePrevious: true)
          |> group()
          |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
          |> map(fn: (r) => ({{
              _time:     r._time,
              rtk:       r["elevation"],
              baro:      r["height"],
              error:     (r["elevation"] - {GEOID_OFFSET}) - r["height"]
          }}))
          |> filter(fn: (r) => exists r.rtk and exists r.baro)
          |> sort(columns: ["_time"], desc: false)
        """

        accuracy_tables = query_api.query(accuracy_query)

        print(f"\n   {'TIMESTAMP':<25} | {'RTK-Adj (m)':<12} | {'BARO (m)':<10} | {'ERROR':<10}")
        print("   " + "-" * 65)

        errors      = []
        rows_printed = 0
        last_alt    = -999.0

        for table in accuracy_tables:
            for record in table:
                t_str = record["_time"].strftime("%H:%M:%S")
                rtk   = (record["rtk"] - GEOID_OFFSET) if record["rtk"] is not None else 0.0
                baro  = record["baro"] if record["baro"] is not None else 0.0
                err   = record["error"] if record["error"] is not None else 0.0

                # Motion filter: only print rows where altitude changed > 0.5 m
                if abs(rtk - last_alt) > 0.5 or rows_printed < 5:
                    errors.append(abs(err))
                    marker = "⚠️ DRIFT" if abs(err) > 1.0 else ""
                    print(f"   {t_str:<25} | {rtk:>12.3f} | {baro:>10.3f} | {err:>10.3f}  {marker}")
                    last_alt     = rtk
                    rows_printed += 1

                if rows_printed > 25:
                    break

        if errors:
            mean_err = statistics.mean(errors)
            print("   " + "-" * 65)
            print(f"   📊 CALIBRATION STATUS: Mean Error = {mean_err:.3f} m")

            if mean_err < 0.5:
                print("   ✅ SYSTEM OPTIMISED: Geoid offset is well-calibrated.")
            else:
                print(f"   ⚠️  RESIDUAL DRIFT: Consider adjusting GEOID_OFFSET in this script.")
                print(f"       Suggested new value: GEOID_OFFSET = {mean_err:.2f}")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_bucket()
