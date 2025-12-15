import os
import subprocess

# ==============================================================================
# Script: fix_playback_login.py
# Purpose: Fixes the FileBrowser database path mismatch.
#          Remounts the database to '/filebrowser.db' so the app can find the
#          'admin' user we created.
# ==============================================================================

COMPOSE_FILE = "docker/docker-compose.yml"

def main():
    print("🔐 FIXING PLAYBACK AUTHENTICATION...")

    # 1. Read the current config
    with open(COMPOSE_FILE, "r") as f:
        content = f.read()

    # 2. Patch the volume mount
    # We change the target from /database.db to /filebrowser.db
    if ":/database.db" in content:
        print("   🔧 Aligning database path...")
        new_content = content.replace(":/database.db", ":/filebrowser.db")
        
        with open(COMPOSE_FILE, "w") as f:
            f.write(new_content)
            
        print("   ✅ Configuration patched.")
    else:
        print("   ⚠️  Config already looks correct or different. Proceeding to restart...")

    # 3. Restart the Playback Server
    print("   🔄 Restarting autel_playback...")
    # We use 'up -d' to apply the configuration change
    subprocess.run("docker compose --env-file .env -f docker/docker-compose.yml up -d autel_playback", shell=True)

    print("\n✅ LOGIN FIX APPLIED")
    print("   -------------------------------------------------")
    print("   👉 Go to: http://localhost:8080")
    print("   👤 User:  admin")
    print("   🔑 Pass:  minimumlengthis12")
    print("   -------------------------------------------------")

if __name__ == "__main__":
    main()
