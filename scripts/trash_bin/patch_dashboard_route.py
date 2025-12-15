import json
import os

# ==============================================================================
# Script Name: patch_dashboard_route.py
# Description: robustly locates and updates Geomap panels in Grafana JSON.
#              - Handles nested panels (Rows).
#              - Switches visualization to 'Route' (Path Line).
#              - Adds 'Drone Position' marker.
# Version:     1.1.0 (Recursive Fix)
# Author:      System Architect (Gemini)
# Date:        2025-12-15
# ==============================================================================

DASHBOARD_PATH = "src/dashboards/autel_engineering_v2.json"

def get_route_layers():
    """Returns the configured map layers for flight path + drone icon."""
    return [
        {
            "type": "route",
            "name": "Flight Path",
            "config": {
                "style": {
                    "color": {"fixed": "#32CD32"}, # Lime Green
                    "opacity": 0.8,
                    "width": 3,
                    "arrow": "forward"
                }
            },
            "location": {"mode": "auto"}
        },
        {
            "type": "markers",
            "name": "Drone Position",
            "config": {
                "style": {
                    "color": {"fixed": "#F2495C"}, # Red
                    "opacity": 1,
                    "size": 10,
                    "symbol": "circle"
                },
                "show": "last" # Only show the current position
            },
            "location": {"mode": "auto"}
        }
    ]

def patch_panel_list(panels):
    """Recursively searches for and patches geomap panels."""
    count = 0
    for panel in panels:
        p_type = panel.get("type", "unknown")
        p_title = panel.get("title", "Untitled")
        
        # recursive check for Rows
        if p_type == "row" and "panels" in panel:
            count += patch_panel_list(panel["panels"])
            continue

        # Found a Map!
        if p_type == "geomap":
            print(f"   🎯 Patching Panel: '{p_title}' (ID: {panel.get('id')})")
            
            # Update Layers
            if "options" not in panel: panel["options"] = {}
            panel["options"]["layers"] = get_route_layers()
            
            # Reset View to Fit Data
            panel["options"]["view"] = {
                "id": "fit",
                "lat": 0,
                "lon": 0,
                "zoom": 1
            }
            count += 1
            
        else:
            # Debug output to see what else is there
            # print(f"      Skipping panel: {p_title} ({p_type})")
            pass
            
    return count

def patch_dashboard():
    print(f"🔍 Reading dashboard: {DASHBOARD_PATH}...")
    
    if not os.path.exists(DASHBOARD_PATH):
        print(f"❌ ERROR: File not found at {DASHBOARD_PATH}")
        return

    try:
        with open(DASHBOARD_PATH, "r") as f:
            dashboard = json.load(f)

        # Start the recursive search
        top_panels = dashboard.get("panels", [])
        total_patched = patch_panel_list(top_panels)

        if total_patched > 0:
            with open(DASHBOARD_PATH, "w") as f:
                json.dump(dashboard, f, indent=2)
            print(f"\n✅ Success! Updated {total_patched} map panel(s).")
            print("   👉 ACTION REQUIRED: Re-import 'src/dashboards/autel_engineering_v2.json' into Grafana to see changes.")
        else:
            print("\n⚠️  Warning: No 'geomap' panels were found in the file.")
            print("   Please verify the dashboard JSON actually contains a Geomap panel.")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    patch_dashboard()
