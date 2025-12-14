"""
-----------------------------------------------------------------------------
Script Name: generate_schema_report.py
Description: Introspects InfluxDB bucket to generate a Markdown schema report.
             NOW INCLUDES: A live preview of the last 5 records per measurement.
Version:     1.2.0 (Added Data Preview Table)
Author:      System Architect
Date:        2025-12-14
-----------------------------------------------------------------------------
"""

import os
import time
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
URL = os.getenv("INFLUX_URL", "http://localhost:8086")
TOKEN = os.getenv("INFLUX_TOKEN", "my-super-secret-token-change-me")
ORG = os.getenv("INFLUX_ORG", "autel_ops")
BUCKET = os.getenv("INFLUX_BUCKET", "telemetry")

def generate_report():
    print(f"🔍 Connecting to InfluxDB at {URL} (Org: {ORG}, Bucket: {BUCKET})...")
    
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    query_api = client.query_api()

    report_lines = []
    report_lines.append(f"# 📊 Autel Mission Control - Data Report")
    report_lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Get Measurements
    print("   ...fetching measurements")
    flux_measurements = f'import "influxdata/influxdb/schema"\n schema.measurements(bucket: "{BUCKET}")'
    
    try:
        tables = query_api.query(flux_measurements)
        measurements = [record.get_value() for table in tables for record in table.records]
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    if not measurements:
        print("⚠️ No data found. Make sure the bridge is running!")
        return

    for m in measurements:
        print(f"   found measurement: {m}")
        report_lines.append(f"## Measurement: `{m}`")
        
        # --- SECTION 2: TAGS ---
        report_lines.append(f"### 🏷️ Tags (Indexed)")
        report_lines.append("| Tag Key | Example Value |")
        report_lines.append("|---|---|")
        
        flux_tags = f'''
        import "influxdata/influxdb/schema"
        schema.measurementTagKeys(bucket: "{BUCKET}", measurement: "{m}")
        '''
        tag_tables = query_api.query(flux_tags)
        tags = [r.get_value() for t in tag_tables for r in t.records]
        
        if tags:
            for tag in tags:
                # Get a sample value for the tag to make it useful
                val_flux = f'''
                from(bucket: "{BUCKET}") 
                |> range(start: -24h) 
                |> filter(fn: (r) => r["_measurement"] == "{m}") 
                |> keep(columns: ["{tag}"]) 
                |> limit(n:1)
                '''
                val_res = query_api.query(val_flux)
                example = "N/A"
                if val_res and len(val_res) > 0 and len(val_res[0].records) > 0:
                    example = val_res[0].records[0][tag]
                
                report_lines.append(f"| **{tag}** | `{example}` |")
        else:
            report_lines.append("| *None* | - |")
        report_lines.append("")

        # --- SECTION 3: FIELDS ---
        report_lines.append(f"### 🔢 Fields (Metrics)")
        report_lines.append("| Field Key | Data Type |")
        report_lines.append("|---|---|")

        flux_fields = f'''
        import "influxdata/influxdb/schema"
        schema.measurementFieldKeys(bucket: "{BUCKET}", measurement: "{m}")
        '''
        field_tables = query_api.query(flux_fields)
        fields = [r.get_value() for t in field_tables for r in t.records]

        for field in fields:
            # Check type by grabbing last point
            type_flux = f'''
            from(bucket: "{BUCKET}") 
            |> range(start: -24h) 
            |> filter(fn: (r) => r["_measurement"] == "{m}")
            |> filter(fn: (r) => r["_field"] == "{field}")
            |> last()
            '''
            try:
                type_res = query_api.query(type_flux)
                if type_res and len(type_res) > 0 and len(type_res[0].records) > 0:
                    val = type_res[0].records[0].get_value()
                    val_type = type(val).__name__
                else:
                    val_type = "unknown"
            except:
                val_type = "unknown"
                
            report_lines.append(f"| {field} | {val_type} |")
        
        report_lines.append("")

        # --- SECTION 4: DATA PREVIEW (The new part) ---
        report_lines.append(f"### 📋 Recent Data Preview (Last 5 Lines)")
        
        # Pivot query to get a readable "Table" view
        preview_flux = f'''
        from(bucket: "{BUCKET}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "{m}")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 5)
        '''
        
        preview_tables = query_api.query(preview_flux)
        
        if preview_tables:
            # Dynamically build header from the first record found
            # We want specific order: Time, Tags, then Fields
            first_record = preview_tables[0].records[0]
            all_keys = first_record.values.keys()
            
            # Exclude internal keys
            exclude = ["result", "table", "_start", "_stop", "_measurement"]
            display_keys = [k for k in all_keys if k not in exclude]
            
            # Sort: put _time first
            if "_time" in display_keys:
                display_keys.remove("_time")
                display_keys.insert(0, "_time")
            
            # Create Markdown Header
            header_str = "| " + " | ".join(display_keys) + " |"
            separator_str = "| " + " | ".join(["---"] * len(display_keys)) + " |"
            report_lines.append(header_str)
            report_lines.append(separator_str)
            
            # Print Rows
            for table in preview_tables:
                for record in table.records:
                    row_vals = []
                    for key in display_keys:
                        val = record[key]
                        # Format timestamp nicely
                        if key == "_time":
                            val = val.strftime('%H:%M:%S')
                        # Round floats to 4 decimals for readability
                        elif isinstance(val, float):
                            val = round(val, 4)
                        row_vals.append(str(val))
                    report_lines.append("| " + " | ".join(row_vals) + " |")
        else:
            report_lines.append("*No recent data found.*")

        report_lines.append("\n---\n")

    # Write to file
    with open("DATA_SCHEMA.md", "w") as f:
        f.write("\n".join(report_lines))
    
    print("\n✅ Success! Detailed report saved to 'DATA_SCHEMA.md'")

if __name__ == "__main__":
    generate_report()
