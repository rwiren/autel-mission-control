import json
import os
import re

# ==============================================================================
# Script Name: fix_map_pathing.py
# Description: Fixes the "Spiderweb/Blob" effect on the Live Map.
#              1. Updates the Flux query to GROUP and SORT data (Critical for lines).
#              2. Configures the Geomap panel to explicitly use 'lat'/'lon'.
# Version:     1.3.0 (Flux Sorting & Grouping Fix)
# Author:      System Architect
# ==============================================================================

DASHBOARD_PATH = "src/dashboards/autel_engineering_v2.json"

# The Optimized Flux Query (Single Stream, Time-Sorted)
NEW_FLUX_QUERY = """from(bucket: "telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "data_latitude" or r["_field"] == "data_longitude")
  // CRITICAL FIX 1: Group all data into one table to prevent fragmentation
  |> group()
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  // Filter out nulls and 0.0 (Null Island)
  |> filter(fn: (r) => exists r["data_latitude"] and exists r["data_longitude"])
  |> filter(fn: (r) => r["data_latitude"] != 0.0 and r["data_longitude"] != 0.0)
  |> map(fn: (r) => ({
      _time: r._time,
      lat: r.data_latitude,
      lon: r.data_longitude
  }))
  // CRITICAL FIX 2: Sort by time to draw a clean line
  |> sort(columns: ["_time"])"""

def get_clean_layers():
    return [
        {
            "name": "Flight Path",
            "type": "route",
            "config": {
                "style": {
                    "color": {"fixed": "#32CD32"}, # Lime Green
                    "opacity": 0.8,
                    "width": 3,
                    "arrow": "forward"
                }
            },
            # Explicit mapping to match the 'map' output in Flux
            "location": {
                "mode": "coords",
                "latitude": "lat",
                "longitude": "lon"
            }
        },
        {
            "name": "Current Pos",
            "type": "markers",
            "config": {
                "style": {
                    "color": {"fixed": "#F2495C"}, # Red Dot
                    "opacity": 1,
                    "size": 10,
                    "symbol": "circle"
                },
                "show": "last"
            },
            "location": {
                "mode": "coords",
                "latitude": "lat",
                "longitude": "lon"
            }
        }
    ]

def patch_dashboard():
    print(f"🔍 Reading dashboard: {DASHBOARD_PATH}...")
    
    if not os.path.exists(DASHBOARD_PATH):
        print(f"❌ ERROR: File not found at {DASHBOARD_PATH}")
        print("   👉 Please export your 'Live views' dashboard to this path first.")
        return

    with open(DASHBOARD_PATH, "r") as f:
        dashboard = json.load(f)

    def update_panels(panels):
        count = 0
        for p in panels:
            if p.get("type") == "row" and "panels" in p:
                count += update_panels(p["panels"])
            
            elif p.get("type") == "geomap":
                print(f"   🎯 Patching Map: '{p.get('title')}'")
                
                # 1. Update the Query Logic
                if "targets" in p and len(p["targets"]) > 0:
                    p["targets"][0]["query"] = NEW_FLUX_QUERY
                    print("      ✅ Injected Optimized Flux Query (Grouped & Sorted)")
                
                # 2. Update the Visual Layers
                if "options" not in p: p["options"] = {}
                p["options"]["layers"] = get_clean_layers()
                
                # 3. Force View Fit
                p["options"]["view"] = {"id": "fit", "lat": 0, "lon": 0, "zoom": 1}
                
                count += 1
        return count

    total = update_panels(dashboard.get("panels", []))

    if total > 0:
        with open(DASHBOARD_PATH, "w") as f:
            json.dump(dashboard, f, indent=2)
        print(f"\n✅ Success! Patched {total} map panel(s).")
        print("   👉 ACTION: Re-import 'src/dashboards/autel_engineering_v2.json' into Grafana.")
    else:
        print("⚠️  Warning: No Geomap panel found.")

if __name__ == "__main__":
    patch_dashboard()
