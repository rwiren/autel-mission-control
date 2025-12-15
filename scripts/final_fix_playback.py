import os
import subprocess
import time

# ==============================================================================
# Script: final_fix_playback.py
# Purpose: Resolves the "Wrong Credentials" loop by aligning paths.
#          1. Standardizes mount to '/filebrowser.db'.
#          2. Wipes the database to ensure a clean state.
#          3. Creates the user in the CORRECT location.
# ==============================================================================

COMPOSE_FILE = "docker/docker-compose.yml"
DB_FILE = "config/filebrowser.db"

def run_cmd(cmd):
    print(f"   > {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def main():
    print("🔓 EXECUTING FINAL PLAYBACK FIX...")

    # 1. Stop the container to release file locks
    print("\n[1/5] Stopping Service...")
    run_cmd("docker stop autel_playback")
    run_cmd("docker rm autel_playback")

    # 2. Reset the Database File (Clean Slate)
    print("\n[2/5] Wiping Database File...")
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    # Create fresh empty file
    open(DB_FILE, "a").close()
    print(f"   ✅ Recreated {DB_FILE}")

    # 3. Fix Docker Compose (Force Default Path)
    print("\n[3/5] Aligning Configuration...")
    with open(COMPOSE_FILE, "r") as f:
        content = f.read()
    
    # We replace ANY incorrect mount with the standard '/filebrowser.db'
    if ":/database.db" in content:
        content = content.replace(":/database.db", ":/filebrowser.db")
        with open(COMPOSE_FILE, "w") as f:
            f.write(content)
        print("   ✅ Fixed mount point to ':/filebrowser.db'")
    elif ":/filebrowser.db" in content:
        print("   ℹ️  Mount point is already correct.")
    else:
        print("   ⚠️  Warning: Check docker-compose.yml manually.")

    # 4. Start the Container
    print("\n[4/5] Starting Service...")
    run_cmd("docker compose --env-file .env -f docker/docker-compose.yml up -d playback_server")
    
    print("   ⏳ Waiting 10s for application to initialize...")
    time.sleep(10)

    # 5. Create User (Targeting the Default Path)
    print("\n[5/5] creating 'admin' user...")
    
    # Init first
    run_cmd("docker exec autel_playback filebrowser -d /filebrowser.db config init")
    # Set Permission
    run_cmd("docker exec autel_playback filebrowser -d /filebrowser.db users add admin minimumlengthis12 --perm.admin")

    print("\n✅ REPAIR COMPLETE")
    print("   -------------------------------------------------")
    print("   PLEASE FOLLOW THESE STEPS EXACTLY:")
    print("   1. Open: http://localhost:8080")
    print("   2. PRESS 'CTRL + R' (Windows) or 'CMD + R' (Mac) to clear cache.")
    print("   3. User: admin")
    print("   4. Pass: minimumlengthis12")
    print("   -------------------------------------------------")

if __name__ == "__main__":
    main()
