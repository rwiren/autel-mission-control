#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: generate_schema_report.py
Description: Connects to InfluxDB, infers the schema of the DJI telemetry
             measurement, and writes a JSON report suitable for building
             Grafana dashboards.
             Targets the 'drone_telemetry' bucket populated by the Telegraf
             MQTT consumer (DJI Cloud API source).
Version:     1.0.0
Author:      RW
Date:        2026-04-05
-----------------------------------------------------------------------------
Usage:
    python3 generate_schema_report.py
    # Output: dji_schema_report.json (in the current working directory)

Configuration:
    Set INFLUX_TOKEN via environment variable:
        export INFLUX_TOKEN="your-token-here"

Dependencies:
    pip install influxdb-client
-----------------------------------------------------------------------------
"""

import os
import json
from influxdb_client import InfluxDBClient

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
INFLUX_URL    = "http://localhost:8086"
INFLUX_ORG    = "dji_ops"
INFLUX_BUCKET = "drone_telemetry"

INFLUX_TOKEN  = os.getenv("INFLUX_TOKEN", "my-super-secret-token-change-me")

REPORT_FILE   = "dji_schema_report.json"

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def generate_report():
    print(f"🔍 Connecting to InfluxDB at {INFLUX_URL}")
    print(f"   Org: {INFLUX_ORG}  |  Bucket: {INFLUX_BUCKET}\n")

    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG,
        timeout=30_000  # 30 s — increased for large datasets
    )
    query_api = client.query_api()
    schema_data = {}

    try:
        # -------------------------------------------------------------------
        # Step 1: List all measurements in the bucket
        # -------------------------------------------------------------------
        print("   [1/4] Fetching measurements...")
        measurements_query = f"""
        import "influxdata/influxdb/schema"
        schema.measurements(bucket: "{INFLUX_BUCKET}")
        """
        tables       = query_api.query(measurements_query)
        measurements = [r.get_value() for t in tables for r in t]

        if not measurements:
            print("❌ No measurements found. Start the DJI telemetry ingestion first.")
            return

        for m in measurements:
            print(f"   Found measurement: {m}")
            schema_data[m] = {"fields": [], "tags": [], "recent_values": {}}

        # -------------------------------------------------------------------
        # Step 2: Tag keys per measurement
        # -------------------------------------------------------------------
        print("\n   [2/4] Fetching tag keys...")
        for m in measurements:
            tag_query = f"""
            import "influxdata/influxdb/schema"
            schema.measurementTagKeys(bucket: "{INFLUX_BUCKET}", measurement: "{m}")
            """
            for t in query_api.query(tag_query):
                for r in t:
                    schema_data[m]["tags"].append(r.get_value())

        # -------------------------------------------------------------------
        # Step 3: Field keys per measurement
        # -------------------------------------------------------------------
        print("   [3/4] Fetching field keys...")
        for m in measurements:
            field_query = f"""
            import "influxdata/influxdb/schema"
            schema.measurementFieldKeys(bucket: "{INFLUX_BUCKET}", measurement: "{m}")
            """
            for t in query_api.query(field_query):
                for r in t:
                    schema_data[m]["fields"].append(r.get_value())

        # -------------------------------------------------------------------
        # Step 4: Sample values (most recent 5 rows per measurement)
        # -------------------------------------------------------------------
        print("   [4/4] Fetching preview data...")
        for m in measurements:
            preview_query = f"""
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -24h)
              |> filter(fn: (r) => r["_measurement"] == "{m}")
              |> limit(n: 5)
            """
            for t in query_api.query(preview_query):
                for r in t:
                    field = r.get_field()
                    value = r.get_value()
                    if field and field not in schema_data[m]["recent_values"]:
                        schema_data[m]["recent_values"][field] = value

        # -------------------------------------------------------------------
        # Save report
        # -------------------------------------------------------------------
        with open(REPORT_FILE, "w") as f:
            json.dump(schema_data, f, indent=4)

        print(f"\n✅ Schema report saved: {REPORT_FILE}")
        print("   Use this JSON to map your Grafana panels to the correct field names.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    generate_report()
