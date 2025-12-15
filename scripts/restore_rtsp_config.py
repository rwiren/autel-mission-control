import os
import subprocess
import time

# ==============================================================================
# Script: restore_rtsp_config.py
# Purpose: Restoration script for the MediaMTX configuration.
#          1. Writes a syntax-perfect mediamtx.yml (v3.1.0).
#          2. Restarts the crashed container.
#          3. Checks logs to ensure it stays up.
# ==============================================================================

CONFIG_PATH = "config/mediamtx.yml"

# This configuration uses 600s (10 min) segments and fmp4 safety.
# We write it via Python to avoid Copy-Paste indentation errors.
YAML_CONTENT = """
################################################################################
# AUTEL MISSION CONTROL - RTSP SERVER CONFIGURATION
# Version: 3.1.0
# Created via: restore_rtsp_config.py
################################################################################

paths:
  all:
    readUser: ""
    readPass: ""

  live/rtsp-drone1:
    # Source is pushed from NGINX or Drone
    source: publisher

    # --- DVR Recording Settings ---
    record: yes
    # Save to: recordings/live/rtsp-drone1/YYYY-MM-DD_HH-MM-SS.mp4
    recordPath: ./recordings/%path/%Y-%m-%d_%H-%M-%S.mp4
    
    # Format: Fragmented MP4 (Safe against power loss)
    recordFormat: fmp4
    
    # Segment Duration: 10 Minutes (Prevents file clutter)
    recordPartDuration: 600s
    
    # Keep recordings forever (0s)
    recordDeleteAfter: 0s

    # --- Timeouts ---
    # Wait 20s after signal loss before closing file
    readTimeout: 20s
    writeTimeout: 20s

  all_others:
    record: no
"""

def main():
    print("🚑 RESTORING RTSP CONFIGURATION...")

    # 1. Write the Config File
    try:
        with open(CONFIG_PATH, "w") as f:
            f.write(YAML_CONTENT.strip())
        print(f"   ✅ Configuration written to {CONFIG_PATH}")
    except Exception as e:
        print(f"   ❌ Failed to write config: {e}")
        return

    # 2. Restart the Container
    print("\n🔄 Restarting autel_rtsp container...")
    subprocess.run("docker restart autel_rtsp", shell=True)
    
    # 3. Wait and Verify
    print("   ⏳ Waiting 5 seconds to verify stability...")
    time.sleep(5)
    
    # Check if it is actually running
    result = subprocess.run("docker ps --filter name=autel_rtsp --format '{{.Status}}'", 
                            shell=True, capture_output=True, text=True)
    
    status = result.stdout.strip()
    
    if "Up" in status and "Restarting" not in status:
        print(f"   ✅ SUCCESS: Container is Online ({status})")
        print("   -------------------------------------------------")
        print("   Your system is ready. The 'Restart Loop' is fixed.")
        print("   Recordings will now be 10 minutes long.")
        print("   -------------------------------------------------")
    else:
        print(f"   ❌ FAILURE: Container is {status}")
        print("   🔍 Fetching crash logs...")
        subprocess.run("docker logs autel_rtsp", shell=True)

if __name__ == "__main__":
    main()
