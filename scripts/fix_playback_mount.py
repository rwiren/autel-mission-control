import os
import subprocess

# ==============================================================================
# Script: fix_playback_mount.py
# Purpose: Fixes the persistent login loop by aligning the database mount.
#          1. Updates docker-compose.yml to mount the DB to '/database.db' (Default)
#          2. Removes conflicting anonymous volumes.
#          3. Re-applies the user credentials to the correct location.
# ==============================================================================

COMPOSE_FILE = "docker/docker-compose.yml"
DB_FILE = "config/filebrowser.db"

def main():
    print("🔐 FIXING PLAYBACK DATABASE MOUNT...")

    # 1. Update Docker Compose
    # We need to map the local file to the INTERNAL path '/database.db'
    print("[1/4] patching docker-compose.yml...")
    with open(COMPOSE_FILE, "r") as f:
        content = f.read()

    # Replace the incorrect mount point
    if ":/filebrowser.db" in content:
        new_content = content.replace(":/filebrowser.db", ":/database.db")
        with open(COMPOSE_FILE, "w") as f:
            f.write(new_content)
        print("   ✅ Changed mount to ':/database.db' (Standard Path)")
    elif ":/database.db" in content:
        print("   ℹ️  Mount path already correct.")
    else:
        print("   ⚠️  Could not find mount pattern. Please check file manually.")

    # 2. Hard Restart (Recreate Container)
    print("\n[2/4] Recreating Playback Container...")
    # Stop and remove to clear any anonymous volume bindings
    subprocess.run("docker stop autel_playback", shell=True)
    subprocess.run("docker rm autel_playback", shell=True)
    # Bring it back up with the new config
    subprocess.run("docker compose --env-file .env -f docker/docker-compose.yml up -d playback_server", shell=True)

    # 3. Wait for Init
    print("   ⏳ Waiting 5s for container initialization...")
    subprocess.run("sleep 5", shell=True)

    # 4. Re-Apply User (Just in case)
    print("\n[3/4] Ensuring Admin User Exists...")
    # Now we execute against the STANDARD path '/database.db'
    cmd = "docker exec autel_playback filebrowser -d /database.db users add admin minimumlengthis12 --perm.admin"
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    
    if "ID" in result.stdout or "admin" in result.stdout:
        print("   ✅ User 'admin' confirmed.")
    elif "already exists" in result.stderr:
         # If user exists, we force update the password to be sure
         print("   ℹ️  User exists. Updating password...")
         subprocess.run("docker exec autel_playback filebrowser -d /database.db users update admin --password minimumlengthis12", shell=True)
    else:
        print(f"   ⚠️  Note: {result.stderr.strip()}")

    print("\n✅ REPAIR COMPLETE")
    print("   -------------------------------------------------")
    print("   👉 Go to: http://localhost:8080")
    print("   👤 User:  admin")
    print("   🔑 Pass:  minimumlengthis12")
    print("   -------------------------------------------------")

if __name__ == "__main__":
    main()
