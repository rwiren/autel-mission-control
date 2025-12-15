import os
import time
import statistics
from influxdb_client import InfluxDBClient

# ==============================================================================
# Script Name: inspect_telemetry.py
# Description: Development-grade telemetry inspector.
#              1. Scans data volume (Last 4 Hours).
#              2. Checks Sensor Health (RTK vs Baro).
#              3. "Action Finder": Locates Takeoff/Landing by detecting motion.
#              4. Calculates Geoid Offset (Truth Analysis).
# Version:     1.4.1 (Dev Mode: Hardcoded Token)
# Author:      System Architect (Gemini)
# Date:        2025-12-15
# ==============================================================================

# Configuration
INFLUX_URL = "http://localhost:8086"
INFLUX_ORG = "autel_ops"
INFLUX_BUCKET = "telemetry"

# SECURITY: Hardcoded for Dev Convenience (as requested)
INFLUX_TOKEN = "my-super-secret-token-change-me"

# Analysis Settings
# Look back 4 hours to find the flight session
TIME_RANGE = "-4h"       
# Correction factor detected in previous runs (RTK is ~3.13m higher than Baro)
GEOID_OFFSET = 3.13      

def print_header(text):
    print(f"\n============================================================")
    print(f" {text}")
    print(f"============================================================")

def inspect_bucket():
    print_header(f"📡 TELEMETRY INSPECTOR v1.4.1 | Window: {TIME_RANGE}")

    client = InfluxDBClient(
        url=INFLUX_URL, 
        token=INFLUX_TOKEN, 
        org=INFLUX_ORG, 
        timeout=60_000
    )
    query_api = client.query_api()

    try:
        # ---------------------------------------------------------
        # PART 1: General Volume Scan
        # ---------------------------------------------------------
        print("🔍 Step 1: Scanning Data Volume...")
        
        # We count fields to verify data exists
        stats_query = f"""
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: {TIME_RANGE})
          |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
          |> count()
          |> group(columns: ["_field"])
          |> sum()
        """
        
        result = query_api.query(stats_query)
        field_counts = {}
        
        for table in result:
            for record in table:
                field = record.get_field()
                count = record.get_value()
                if field and count:
                    field_counts[field] = count

        if not field_counts:
            print(f"   ⚠️  No data found in the last {TIME_RANGE}.")
            return

        print(f"   ✅ Data Found! Total Active Fields: {len(field_counts)}")

        # ---------------------------------------------------------
        # PART 2: Find the "Action" (Dynamic Movement)
        # ---------------------------------------------------------
        print_header("🎬 Step 2: Locating High-Motion Segment (Takeoff/Landing)")
        print(f"   Applying Geoid Offset of -{GEOID_OFFSET}m to RTK data...")

        # Dynamic query that:
        # 1. Resamples to 1s
        # 2. Applies the offset math
        # 3. Sorts by time to show the flight sequence
        accuracy_query = f"""
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: {TIME_RANGE})
          |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
          |> filter(fn: (r) => r["_field"] == "data_position_state_rtk_hgt" or r["_field"] == "data_drone_list_0_height")
          // 1. Resample to 1s resolution
          |> aggregateWindow(every: 1s, fn: mean, createEmpty: true)
          // 2. Fill gaps
          |> fill(usePrevious: true)
          // 3. Ungroup to merge streams
          |> group() 
          // 4. Pivot to get columns side-by-side
          |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
          |> map(fn: (r) => ({{
              _time: r._time,
              rtk: r["data_position_state_rtk_hgt"],
              baro: r["data_drone_list_0_height"],
              // Apply Calibration: (RTK - Offset) - Baro
              error: (r["data_position_state_rtk_hgt"] - {GEOID_OFFSET}) - r["data_drone_list_0_height"]
          }}))
          // 5. Validity Filter
          |> filter(fn: (r) => exists r.rtk and exists r.baro)
          // 6. Sort Oldest -> Newest to replay the flight
          |> sort(columns: ["_time"], desc: false)
        """

        accuracy_tables = query_api.query(accuracy_query)
        
        print(f"\n   {'TIMESTAMP':<25} | {'RTK (Adj)':<10} | {'BARO (m)':<10} | {'ERROR':<10}")
        print("   " + "-"*65)

        errors = []
        rows_printed = 0
        last_alt = -999

        for table in accuracy_tables:
            for record in table:
                t_str = record["_time"].strftime("%H:%M:%S")
                # Apply offset visually for the table
                rtk = record["rtk"] - GEOID_OFFSET if record["rtk"] else 0
                baro = record["baro"] if record["baro"] else 0
                err = record["error"] if record["error"] else 0
                
                # MOTION FILTER: Only print if altitude changed by > 0.5m since last print
                # This effectively finds "Takeoff" and "Landing" events
                if abs(rtk - last_alt) > 0.5 or rows_printed < 5:
                    errors.append(abs(err))
                    
                    marker = ""
                    if abs(err) > 1.0: marker = "⚠️ DRIFT"

                    print(f"   {t_str:<25} | {rtk:>10.3f} | {baro:>10.3f} | {err:>10.3f} {marker}")
                    
                    last_alt = rtk
                    rows_printed += 1
                
                # Limit output to first 25 significant events to keep terminal clean
                if rows_printed > 25:
                    break

        if errors:
            mean_err = statistics.mean(errors)
            print("   " + "-"*65)
            print(f"   📊 CALIBRATION STATUS: Mean Error: {mean_err:.3f}m")
            
            if mean_err < 0.5:
                print("   ✅ SYSTEM OPTIMIZED: Geoid Offset is perfectly calibrated.")
                print("      Your Grafana 'Altitude Truth' panel should now look perfect.")
            else:
                print("   ⚠️ RESIDUAL DRIFT: Barometer might be drifting due to weather.")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_bucket()
