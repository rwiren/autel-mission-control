"""
SCRIPT: src/check_stream.py
VERSION: 1.0.0
DESCRIPTION: Verifies if the MediaMTX server is receiving an RTMP stream.
"""
import requests
import sys

# MediaMTX API URL (Default API port is 9997, but we didn't expose it in docker-compose)
# Alternative: Check the HTTP Stream endpoint status
STREAM_URL = "http://localhost:8888/drone/index.m3u8"

print(f"📡 Checking Video Stream Status...")
print(f"   Target: {STREAM_URL}")
print("-" * 40)

try:
    response = requests.head(STREAM_URL, timeout=2)
    
    if response.status_code == 200:
        print("✅ STREAM IS LIVE! (HTTP 200)")
        print("   The drone video is reaching the server.")
        print("   Check Grafana Dashboard now.")
    elif response.status_code == 404:
        print("⚠️  Stream Not Found (HTTP 404)")
        print("   The server is running, but NO video is being pushed.")
        print("   Action: Check Autel Controller RTMP settings.")
    else:
        print(f"❌ Unexpected Status: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("❌ Connection Refused.")
    print("   Is the 'autel_video' container running?")

print("-" * 40)
