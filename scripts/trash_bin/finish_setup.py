import os
import json
import urllib.request
import urllib.error
import base64

# ==============================================================================
# Script: finish_setup.py
# Purpose: finishes the deployment by uploading the dashboard using 
#          credentials explicitly read from the .env file.
# ==============================================================================

ENV_FILE = ".env"
DASHBOARD_FILE = "src/dashboards/autel_engineering_v2.json"
GRAFANA_URL = "http://localhost:3000"

def load_env_manual():
    """Manually parses .env file to ensure we get the real password."""
    creds = {"GRAFANA_USER": "admin", "GRAFANA_PASS": "admin"}
    if os.path.exists(ENV_FILE):
        print(f"🔍 Reading credentials from {ENV_FILE}...")
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key in creds:
                        creds[key] = value
    return creds

def main():
    # 1. Load Credentials
    creds = load_env_manual()
    user = creds["GRAFANA_USER"]
    password = creds["GRAFANA_PASS"]
    print(f"🔐 Authenticating as user: {user}")

    # 2. Load Dashboard
    if not os.path.exists(DASHBOARD_FILE):
        print(f"❌ Error: {DASHBOARD_FILE} not found.")
        return

    with open(DASHBOARD_FILE, "r") as f:
        data = json.load(f)
    
    # 3. Prepare Request
    data["id"] = None # Reset ID to allow import
    payload = {"dashboard": data, "overwrite": True}
    json_data = json.dumps(payload).encode('utf-8')
    
    auth_str = f"{user}:{password}"
    b64_auth = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
    
    req = urllib.request.Request(
        f"{GRAFANA_URL}/api/dashboards/db",
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {b64_auth}'
        },
        method='POST'
    )

    # 4. Send
    try:
        with urllib.request.urlopen(req) as r:
            if r.status == 200:
                print("\n✅ SUCCESS: Dashboard restored!")
                print(f"   👉 Open {GRAFANA_URL} and log in with '{password}'")
    except urllib.error.HTTPError as e:
        if e.code == 401:
             print("\n❌ AUTH FAILED. Please double-check the password in .env")
        else:
             print(f"\n❌ Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")

if __name__ == "__main__":
    main()
