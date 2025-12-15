import os
import subprocess

# ==============================================================================
# Script: fix_recording_segments.py
# Purpose: Fixes the issue where recordings are split into tiny 4-second files.
#          Updates mediamtx.yml to force 10-minute file segments.
# ==============================================================================

CONFIG_FILE = "config/mediamtx.yml"

def main():
    print("📼 OPTIMIZING DVR SEGMENTATION...")

    # 1. Read current config
    try:
        with open(CONFIG_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: {CONFIG_FILE} not found. Are you in the project root?")
        return

    # 2. Modify the config safely
    new_lines = []
    found_part_duration = False

    for line in lines:
        # If we find an existing duration setting, update it
        if "recordPartDuration" in line:
            new_lines.append("    recordPartDuration: 10m\n")
            found_part_duration = True
            print("   ✅ Updated existing recordPartDuration to 10m")
        # If we find the record path, ensure the duration setting follows it
        elif "recordPath:" in line and not found_part_duration:
            new_lines.append(line)
            # Add the setting if it was missing completely
            new_lines.append("    recordPartDuration: 10m\n")
            found_part_duration = True
            print("   ✅ Added missing recordPartDuration: 10m")
        else:
            new_lines.append(line)

    # 3. Write back
    with open(CONFIG_FILE, "w") as f:
        f.writelines(new_lines)

    # 4. Restart Video Server
    print("\n🔄 Restarting Video Server to apply changes...")
    subprocess.run("docker restart autel_rtsp", shell=True)

    print("\n✅ FIXED.")
    print("   -------------------------------------------------")
    print("   Future recordings will now be single, large files.")
    print("   (Existing small files remain as they are)")
    print("   -------------------------------------------------")

if __name__ == "__main__":
    main()
