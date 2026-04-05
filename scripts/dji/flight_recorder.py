#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: flight_recorder.py
Description: Records all incoming DJI Cloud API MQTT telemetry to a
             timestamped JSONL log file for offline analysis and replay.
             Subscribes to 'thing/product/+/osd' (same Cloud API topic
             structure used by both DJI and Autel).
Version:     1.0.0
Author:      RW
Date:        2026-04-05
-----------------------------------------------------------------------------
Usage:
    python3 flight_recorder.py
    # Output: dji_flight_logs/flight_YYYYMMDD_HHMMSS.jsonl

Dependencies:
    pip install paho-mqtt
-----------------------------------------------------------------------------
"""

import paho.mqtt.client as mqtt
import datetime
import os

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
BROKER_ADDRESS = "localhost"
BROKER_PORT    = 1883

# DJI Cloud API OSD topic (telemetry state data)
SUBSCRIBE_TOPIC = "thing/product/+/osd"

# Output directory for log files
LOG_DIR = "dji_flight_logs"

# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

filename = os.path.join(
    LOG_DIR,
    f"flight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
)

# ---------------------------------------------------------------------------
# MQTT CALLBACKS
# ---------------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    """Subscribe to DJI OSD topic once the connection is established."""
    if rc == 0:
        client.subscribe(SUBSCRIBE_TOPIC)
        print(f"✅ Connected to broker at {BROKER_ADDRESS}:{BROKER_PORT}")
        print(f"📡 Subscribed to: {SUBSCRIBE_TOPIC}")
        print(f"📝 Logging to: {filename}")
        print("   Press Ctrl+C to stop.\n")
    else:
        print(f"❌ Connection failed — return code {rc}")

def on_message(client, userdata, msg):
    """Append each received message to the JSONL log file."""
    timestamp = datetime.datetime.now().isoformat()
    with open(filename, "a") as f:
        # Format: ISO timestamp | MQTT topic | raw JSON payload
        f.write(f"{timestamp} | {msg.topic} | {msg.payload.decode('utf-8', errors='replace')}\n")

    # Print a dot per packet so the operator knows data is flowing
    print(".", end="", flush=True)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    client = mqtt.Client(client_id="DJI_FlightRecorder_v1.0", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"🔴 DJI FLIGHT RECORDER v1.0.0 — Starting...")

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Recorder stopped. Log saved: {filename}")
        client.disconnect()
    except ConnectionRefusedError:
        print(f"❌ Connection refused. Is the MQTT broker running on {BROKER_ADDRESS}:{BROKER_PORT}?")

if __name__ == "__main__":
    main()
