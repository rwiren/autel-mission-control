#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: capture_mqtt_schema.py
Description: Connects to the MQTT broker and captures the raw DJI Cloud API
             JSON stream. Performs a deep-merge to build a master schema of
             all possible telemetry fields published by the drone, preserving
             the original nested structure.

             Output: docs/dji_raw_schema.json

             Power on the aircraft before running for best coverage.
Version:     1.0.0
Author:      RW
Date:        2026-04-05
-----------------------------------------------------------------------------
Usage:
    python3 capture_mqtt_schema.py
    # Output: docs/dji_raw_schema.json (created in the docs/ folder relative
    #         to where the script is run from)

DJI Topics sniffed:
    thing/product/+/osd      — Aircraft state
    thing/product/+/events   — Triggered events (warnings, mode changes)

Dependencies:
    pip install paho-mqtt
-----------------------------------------------------------------------------
"""

import json
import time
import sys
import os
import paho.mqtt.client as mqtt

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
BROKER  = "localhost"
PORT    = 1883
TOPICS  = [
    ("thing/product/+/osd",    0),  # Aircraft telemetry (primary stream)
    ("thing/product/+/events", 0),  # Event notifications
]
DURATION = 60  # Capture window in seconds

# Output path (relative to working directory)
OUTPUT_PATH = os.path.join("docs", "dji_raw_schema.json")

# ---------------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------------
master_schema = {}
message_count  = 0

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def deep_merge(source: dict, destination: dict) -> dict:
    """
    Recursively merges `source` into `destination`.

    This builds a complete schema from partial packets by keeping the union
    of all keys ever seen. Lists are kept as the most-recent sample (schema
    approximation — merging heterogeneous lists is out of scope here).
    """
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            # Scalars and lists: keep latest sample
            destination[key] = value
    return destination

# ---------------------------------------------------------------------------
# MQTT CALLBACKS
# ---------------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT broker. Sniffing for {DURATION} seconds...")
        print("⚠️  Power on the drone NOW for best field coverage.\n")
        client.subscribe(TOPICS)
    else:
        print(f"❌ Connection failed — code: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    global master_schema, message_count
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        deep_merge(payload, master_schema)
        message_count += 1
        sys.stdout.write(f"\r📡 Captured packet #{message_count:>4} | Topic: {msg.topic:<50}")
        sys.stdout.flush()
    except json.JSONDecodeError:
        pass  # Ignore non-JSON messages
    except Exception as e:
        print(f"\n[!] Parse error: {e}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)

    client = mqtt.Client(client_id="DJI_SchemaSniffer_v1.0", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    print("🚀 DJI MQTT SCHEMA CAPTURE v1.0.0")
    print(f"   Broker : {BROKER}:{PORT}")
    print(f"   Topics : {[t for t, _ in TOPICS]}")
    print(f"   Output : {OUTPUT_PATH}")
    print("-" * 50)

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()

        # Countdown until capture window closes
        start = time.time()
        while (time.time() - start) < DURATION:
            time.sleep(0.1)

        client.loop_stop()
        print("\n\n✅ Capture complete.")

        # Write merged schema to disk
        with open(OUTPUT_PATH, "w") as f:
            json.dump(master_schema, f, indent=4, sort_keys=True)

        print(f"📄 Schema saved to: {OUTPUT_PATH}")
        print(f"   Total packets merged: {message_count}")

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
        client.loop_stop()

if __name__ == "__main__":
    main()
