import os
import shutil

# ==============================================================================
# Script: cleanup_workspace.py
# Purpose: Safely moves dangerous/obsolete scripts to a 'trash_bin' folder.
#          Works regardless of current directory.
# ==============================================================================

# Files intended for the trash (Dangerous or Obsolete)
TRASH_LIST = [
    # Deployment/Panic Scripts
    "deploy_mission_control.sh",
    "deploy_v0.9.9.sh",
    "upgrade_to_dvr.sh",
    "upgrade_to_dvr_v2.sh",
    "emergency_stabilize.sh",
    "architectural_reset.sh",
    "full_system_recovery.py",
    "restore_system.py",
    "restore_system.sh",
    
    # One-off Fixes
    "fix_live_map.py",
    "fix_map_pathing.py",
    "fix_telemetry.py",
    "fix_datasource.py",
    "patch_dashboard_route.py",
    "finalize_dashboard.py",
    "smart_fix.py",
    "maintenance_rebuild.py",
    "finish_setup.py",
    
    # Old Dashboards (Paths relative to project root, handled separately below)
    "../src/dashboards/autel_dashboard_v1.json",
    "../src/dashboards/autel_dashboard_v3_indoor.json",
    "../src/dashboards/autel_telemetry_master.json"
]

def cleanup():
    # 1. Ensure we are in the 'scripts' folder
    cwd = os.getcwd()
    if not cwd.endswith("scripts"):
        print(f"⚠️  You are currently in: {cwd}")
        print("   Please 'cd scripts' before running this tool.")
        return

    # 2. Create Trash Bin (one level up, in project root, or local? Local is safer for now)
    trash_dir = os.path.join(cwd, "trash_bin")
    if not os.path.exists(trash_dir):
        os.makedirs(trash_dir)
        print(f"📂 Created trash directory: {trash_dir}")

    print("🧹 Moving dangerous/obsolete files...")
    
    count = 0
    for filename in TRASH_LIST:
        # Handle relative paths (like ../src/...)
        src_path = os.path.abspath(os.path.join(cwd, filename))
        file_basename = os.path.basename(src_path)
        dest_path = os.path.join(trash_dir, file_basename)

        if os.path.exists(src_path):
            try:
                shutil.move(src_path, dest_path)
                print(f"   👋 Moved: {filename}")
                count += 1
            except Exception as e:
                print(f"   ❌ Failed to move {filename}: {e}")
        else:
            # Silent skip if file doesn't exist (it's already clean)
            pass

    print(f"\n✅ Cleanup Complete. {count} files moved to 'scripts/trash_bin/'.")
    print("   Your workspace is now safe.")

if __name__ == "__main__":
    cleanup()
