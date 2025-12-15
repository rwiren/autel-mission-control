import json
import os

# ==============================================================================
# Script Name: finalize_dashboard.py
# Description: Injects the "Green Route + Red Dot" visualization into the dashboard.
# Version:     1.2.0 (Live View Fix)
# Author:      System Architect
# ==============================================================================

# TARGET FILE: We assume you want to update the engineering dashboard.
# If your "Live views" dashboard is saved elsewhere, change this path!
DASHBOARD_PATH = "src/dashboards/autel_engineering_v2.json"

def get_mission_control_layers():
    """Returns the dual-layer config for the map."""
    return [
        # LAYER 1: The Breadcrumb Trail (Green Line)
        {
            "type": "route",
            "name": "Flight Path",
            "config": {
                "style": {
                    "color": {"fixed": "#32CD32"},  # Lime Green
                    "opacity": 0.6,
                    "width": 3,
                    "arrow": "forward"
                }
            },
            "location": {"mode": "coords"}
        },
        # LAYER 2: The Drone Itself (Red Dot at current location)
        {
            "type": "markers",
            "name": "Current Pos",
            "config": {
                "style": {
                    "color": {"fixed": "#F2495C"},  # Red
                    "opacity": 1,
                    "size": 10,
                    "symbol": "circle"
                },
                "show": "last"  # <--- MAGIC: Only draws the most recent point
            },
            "location": {"mode": "coords"}
        }
    ]

def patch_dashboard():
    print(f"🔍 Reading dashboard: {DASHBOARD_PATH}...")
    
    if not os.path.exists(DASHBOARD_PATH):
        # Fallback: If the file doesn't exist, we can't patch it.
        # You must export your current Grafana dashboard to this path first!
        print(f"❌ ERROR: File not found at {DASHBOARD_PATH}")
        print("   👉 Please export your 'Live views' dashboard JSON from Grafana")
        print(f"   👉 Save it as '{DASHBOARD_PATH}' and run this script again.")
        return

    with open(DASHBOARD_PATH, "r") as f:
        dashboard = json.load(f)

    panels_patched = 0

    # Recursive function to find panels even inside Rows
    def find_and_patch(panel_list):
        count = 0
        for panel in panel_list:
            # Check if this is a Row (nested panels)
            if panel.get("type") == "row" and "panels" in panel:
                count += find_and_patch(panel["panels"])
            
            # Check if this is our Geomap
            elif panel.get("type") == "geomap":
                print(f"   🎯 Found Map Panel: '{panel.get('title')}'")
                
                # INJECT THE LAYERS
                panel["options"]["layers"] = get_mission_control_layers()
                
                # Ensure view is set to Auto-Fit
                panel["options"]["view"] = {
                    "id": "fit",
                    "lat": 0, "lon": 0, "zoom": 1
                }
                count += 1
        return count

    # Start patching
    panels_patched = find_and_patch(dashboard.get("panels", []))

    if panels_patched > 0:
        with open(DASHBOARD_PATH, "w") as f:
            json.dump(dashboard, f, indent=2)
        print(f"\n✅ Success! Updated {panels_patched} map panel.")
        print("   👉 NEXT STEP: Import 'src/dashboards/autel_engineering_v2.json' back into Grafana.")
    else:
        print("\n⚠️  Warning: No 'geomap' panel found in the file.")

if __name__ == "__main__":
    patch_dashboard()
