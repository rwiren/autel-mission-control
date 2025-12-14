#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script: inspect_telemetry.py
Version: v0.9.5 (Data Science Toolset)
Author: System Architect (Gemini)
Date: 2025-12-14
Description: 
    Deep introspection of the InfluxDB 'telemetry' bucket.
    1. Lists all active Measurements.
    2. Analyzes field types and counts (Data Density).
    3. Detects "Dirty Data" (Zero-Island coordinates: Lat/Lon == 0).
    4. Shows the most recent live packet.

Usage:
    python3 scripts/inspect_telemetry.py
-----------------------------------------------------------------------------
"""

import sys
from datetime import datetime
from influxdb_client import InfluxDBClient

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
# In a production environment, load these from os.environ or .env
URL = "http://localhost:8086"
TOKEN = "my-super-secret-token-change-me"
ORG = "autel_ops"
BUCKET = "telemetry"

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def inspect_bucket():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    query_api = client.query_api()

    print_header("📡 TELEMETRY INSPECTOR v0.9.5")

    # -----------------------------------------------------------------------
    # 1. MEASUREMENT DISCOVERY
    # -----------------------------------------------------------------------
    print("\n🔍 Scanning for Measurements...")
    query_measurements = f'import "influxdata/influxdb/schema" schema.measurements(bucket: "{BUCKET}")'
    
    try:
        tables = query_api.query(query_measurements)
        measurements = [record.get_value() for table in tables for record in table]
        
        if not measurements:
            print("   [!] No measurements found. Bucket is empty.")
            return

        print(f"   Found {len(measurements)} Measurement(s): {', '.join(measurements)}")

    except Exception as e:
        print(f"   [!] Connection Failed: {e}")
        return

    # -----------------------------------------------------------------------
    # 2. FIELD ANALYSIS (Focus on 'mqtt_consumer')
    # -----------------------------------------------------------------------
    target_meas = "mqtt_consumer"
    if target_meas in measurements:
        print_header(f"📊 ANALYSIS: {target_meas}")
        
        # Count total records in last 24h
        count_query = f'''
            from(bucket: "{BUCKET}")
            |> range(start: -24h)
            |> filter(fn: (r) => r["_measurement"] == "{target_meas}")
            |> count()
            |> group(columns: ["_field"])
            |> yield(name: "counts")
        '''
        tables = query_api.query(count_query)
        
        print(f"{'Field Name':<30} | {'Count (24h)':<10}")
        print("-" * 45)
        
        field_names = []
        for table in tables:
            for record in table:
                field = record.get_field()
                count = record.get_value()
                print(f"{field:<30} | {count:<10}")
                field_names.append(field)

        # -------------------------------------------------------------------
        # 3. DIRTY DATA DETECTION (GPS)
        # -------------------------------------------------------------------
        if "data_latitude" in field_names:
            print_header("🧹 QUALITY CHECK: GPS Data")
            
            # Count Zeros (Null Island)
            zero_query = f'''
                from(bucket: "{BUCKET}")
                |> range(start: -24h)
                |> filter(fn: (r) => r["_measurement"] == "{target_meas}")
                |> filter(fn: (r) => r["_field"] == "data_latitude")
                |> filter(fn: (r) => r["_value"] == 0.0)
                |> count()
            '''
            result = query_api.query(zero_query)
            zero_count = 0
            if result:
                 for table in result:
                    for record in table:
                        zero_count = record.get_value()

            print(f"   Checking for 'Null Island' (Lat=0.0)...")
            if zero_count > 0:
                print(f"   ⚠️  WARNING: Found {zero_count} records with invalid GPS (0.0).")
                print("   -> Recommendation: Apply filter in Grafana or clean DB.")
            else:
                print("   ✅ GPS Data looks clean (No zeros found).")

    # -----------------------------------------------------------------------
    # 4. LATEST PACKET DUMP
    # -----------------------------------------------------------------------
    print_header("⏱️  LATEST TELEMETRY SNAPSHOT")
    last_query = f'''
        from(bucket: "{BUCKET}")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "{target_meas}")
        |> last()
    '''
    tables = query_api.query(last_query)
    for table in tables:
        for record in table:
            print(f"   • {record.get_field()}: {record.get_value()}")

if __name__ == "__main__":
    inspect_bucket()
