import json
import os

# ==============================================================================
# Script Name: fix_live_map.py
# Description: Patches the "Live map" panel to fix the "Green Blob" issue.
#              1. Sets Visualization to 'Route' (Green Line).
#              2. Adds a 'Drone Marker' (Red Dot) for the current position.
#              3. EXPLICITLY maps 'lat' and 'lon' fields to fix "Unable to find location".
# Version:     1.2.1 (Fixes Nested Panels & Field Mapping)
# Author:      System Architect
# ==============================================================================

# TARGET FILE: 
# Ensure this matches where you saved your dashboard JSON export
DASHBOARD_PATH = "src/dashboards/autel_engineering_v2.json"

def get_corrected_layers():
    return [
        # LAYER 1: The Flight Path (Green Line)
        {
            "name": "Flight Path",
            "type": "route",
            "config": {
                "style": {
                    "color": {"fixed": "#32CD32"},  # Lime Green
                    "opacity": 0.6,
                    "width": 3,
                    "arrow": "forward"
                }
            },
            # FIX: Explicitly tell Grafana which fields contain coordinates
            "location": {
                "mode": "coords",
                "latitude": "lat",
                "longitude": "lon"
            }
        },
        # LAYER 2: The Drone Icon (Red Dot at Last Position)
        {
            "name": "Current Pos",
            "type": "markers",
            "config": {
                "style": {
                    "color": {"fixed": "#F2495C"},  # Red
                    "opacity": 1,
                    "size": 10,
                    "symbol": "circle"
                },
                "show": "last"  # Only show the most recent point
            },
            # FIX: Explicit mapping here too
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
        print("   👉 Please export your 'Live views' dashboard JSON from Grafana")
        print(f"   👉 Save it as '{DASHBOARD_PATH}' and run this script again.")
        return

    with open(DASHBOARD_PATH, "r") as f:
        dashboard = json.load(f)

    # Recursive function to hunt down the panel
    def find_and_patch(panels):
        count = 0
        for p in panels:
            # If it's a Row, dig deeper
            if p.get("type") == "row" and "panels" in p:
                count += find_and_patch(p["panels"])
            
            # If it's the Map
            elif p.get("type") == "geomap":
                print(f"   🎯 Found Panel: '{p.get('title')}'")
                
                # 1. Update Layers with Explicit Mapping
                if "options" not in p: p["options"] = {}
                p["options"]["layers"] = get_corrected_layers()
                
                # 2. Reset View
                p["options"]["view"] = {"id": "fit", "lat": 0, "lon": 0, "zoom": 1}

                count += 1
        return count

    # Run the search
    total_fixed = find_and_patch(dashboard.get("panels", []))

    if total_fixed > 0:
        with open(DASHBOARD_PATH, "w") as f:
            json.dump(dashboard, f, indent=2)
        print(f"\n✅ Success! Fixed {total_fixed} map panel(s).")
        print("   👉 NEXT STEP: Import 'src/dashboards/autel_engineering_v2.json' back into Grafana (Overwrite).")
    else:
        print("\n⚠️  Warning: Could not find any 'geomap' panel in this file.")
        print("   Double check that you exported the correct dashboard!")

if __name__ == "__main__":
    patch_dashboard()
