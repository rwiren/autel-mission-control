import os
import json
from influxdb_client import InfluxDBClient

# ==============================================================================
# Script Name: generate_schema_report.py
# Description: Connects to InfluxDB, infers the schema of existing measurements,
#              and generates a JSON report for Grafana dashboard building.
# Version:     1.1.1 (Token Fix & Performance Tuning)
# Author:      System Architect (Gemini)
# Date:        2025-12-15
# ==============================================================================

# Configuration
INFLUX_URL = "http://localhost:8086"
# FIXED: Using the actual development token retrieved from the container
INFLUX_TOKEN = "my-super-secret-token-change-me"
INFLUX_ORG = "autel_ops"
INFLUX_BUCKET = "telemetry"

REPORT_FILE = "schema_report.json"

def generate_report():
    print(f"🔍 Connecting to InfluxDB at {INFLUX_URL} (Org: {INFLUX_ORG}, Bucket: {INFLUX_BUCKET})...")
    
    # FIX: Increased timeout to 30s to handle large datasets without crashing
    client = InfluxDBClient(
        url=INFLUX_URL, 
        token=INFLUX_TOKEN, 
        org=INFLUX_ORG,
        timeout=30_000
    )
    
    query_api = client.query_api()
    
    schema_data = {}

    try:
        # 1. Get List of Measurements
        print("   ...fetching measurements")
        # Optimized query using schema package is faster than raw flux
        measurements_query = f"""
        import "influxdata/influxdb/schema"
        schema.measurements(bucket: "{INFLUX_BUCKET}")
        """
        
        tables = query_api.query(measurements_query)
        measurements = [record.get_value() for table in tables for record in table]

        if not measurements:
            print("❌ No measurements found. Please start the telemetry ingestion first.")
            return

        # 2. Inspect Each Measurement
        for m in measurements:
            print(f"   found measurement: {m}")
            schema_data[m] = {
                "fields": [],
                "tags": [],
                "recent_values": {}
            }

            # 3. Get Tag Keys
            tag_query = f"""
            import "influxdata/influxdb/schema"
            schema.measurementTagKeys(bucket: "{INFLUX_BUCKET}", measurement: "{m}")
            """
            tag_tables = query_api.query(tag_query)
            for t_table in tag_tables:
                for t_record in t_table:
                    schema_data[m]["tags"].append(t_record.get_value())

            # 4. Get Field Keys
            field_query = f"""
            import "influxdata/influxdb/schema"
            schema.measurementFieldKeys(bucket: "{INFLUX_BUCKET}", measurement: "{m}")
            """
            field_tables = query_api.query(field_query)
            for f_table in field_tables:
                for f_record in f_table:
                    schema_data[m]["fields"].append(f_record.get_value())

            # 5. Get Preview Data (Optimized)
            # FIX: Added range(start: -24h) to prevent scanning infinite history
            preview_flux = f"""
            from(bucket: "{INFLUX_BUCKET}")
              |> range(start: -24h)
              |> filter(fn: (r) => r["_measurement"] == "{m}")
              |> limit(n:5)
            """
            preview_tables = query_api.query(preview_flux)
            
            for p_table in preview_tables:
                for p_record in p_table:
                    field_name = p_record.get_field()
                    value = p_record.get_value()
                    # Store a sample value to help identify data types
                    if field_name not in schema_data[m]["recent_values"]:
                        schema_data[m]["recent_values"][field_name] = value

        # 6. Save Report
        with open(REPORT_FILE, "w") as f:
            json.dump(schema_data, f, indent=4)
        
        print(f"\n✅ Schema Report generated: {REPORT_FILE}")
        print("   Use this JSON to map your Grafana panels correctly.")

    except Exception as e:
        print(f"\n❌ ERROR: Failed to generate report. {e}")
    finally:
        client.close()

if __name__ == "__main__":
    generate_report()
