import os
import subprocess
import time

# ==============================================================================
# Script: reset_playback_tool.py
# Purpose: Nuke and rebuild the FileBrowser configuration.
#          1. Wipes the corrupt database.
#          2. Fixes docker-compose.yml to mount the DB to the default /filebrowser.db
#          3. Recreates the admin user with your long password.
# ==============================================================================

COMPOSE_FILE = "docker/docker-compose.yml"
DB_FILE = "config/filebrowser.db"

def run_cmd(cmd):
    print(f"   > {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"     ⚠️  Warning: {result.stderr.strip()}")
    return result.stdout.strip()

def main():
    print("🧹 INITIATING PLAYBACK TOOL RESET...")

    # 1. Stop the specific container
    print("\n[1/5] Stopping Playback Service...")
    run_cmd("docker stop autel_playback")
    run_cmd("docker rm autel_playback")

    # 2. Fix the docker-compose.yml mount
    # We need to change ':/database.db' to ':/filebrowser.db'
    print("\n[2/5] Correcting Configuration...")
    with open(COMPOSE_FILE, "r") as f:
        content = f.read()
    
    if ":/database.db" in content:
        new_content = content.replace(":/database.db", ":/filebrowser.db")
        with open(COMPOSE_FILE, "w") as f:
            f.write(new_content)
        print("   ✅ Configuration patched (Mount aligned to /filebrowser.db)")
    else:
        print("   ℹ️  Configuration already looks correct.")

    # 3. Wipe and Recreate Database File
    print("\n[3/5] Wiping Database...")
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    # Create a fresh empty file
    open(DB_FILE, "a").close()
    print("   ✅ Old database deleted. New empty DB created.")

    # 4. Restart the Service (Using the correct service name!)
    print("\n[4/5] Starting Service...")
    run_cmd("docker compose --env-file .env -f docker/docker-compose.yml up -d playback_server")
    
    print("   ⏳ Waiting 5s for database initialization...")
    time.sleep(5)

    # 5. Create User (The "Gold" Step)
    print("\n[5/5] Creating Admin User...")
    
    # Init config inside container
    run_cmd("docker exec autel_playback /filebrowser config init")
    
    # Set config to allow any password
    run_cmd("docker exec autel_playback /filebrowser config set --auth.min-password-length 5")
    
    # Add the user
    # Note: We do NOT use -d /database.db anymore because we fixed the mount to default
    cmd = "docker exec autel_playback /filebrowser users add admin minimumlengthis12 --perm.admin"
    output = run_cmd(cmd)

    if "ID" in output or "admin" in output:
         print("\n✅ SUCCESS! RESET COMPLETE")
         print("   -------------------------------------------------")
         print("   👉 Go to: http://localhost:8080")
         print("   👤 User:  admin")
         print("   🔑 Pass:  minimumlengthis12")
         print("   -------------------------------------------------")
    else:
         print("\n❌ SOMETHING FAILED. CHECK OUTPUT ABOVE.")

if __name__ == "__main__":
    main()
