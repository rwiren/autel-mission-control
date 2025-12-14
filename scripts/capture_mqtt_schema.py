#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script: capture_mqtt_schema.py
Version: v1.0.0 (The Wire Sniffer)
Author: System Architect (Gemini)
Date: 2025-12-14
Description: 
    Connects to the MQTT Broker and captures the RAW JSON stream.
    Performs a "Deep Merge" to construct a Master Schema of ALL possible fields
    sent by the drone, preserving the original nested structure.

    Output: docs/autel_raw_schema.json
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
BROKER = "localhost"
PORT = 1883
# Listen to everything from the drone
TOPICS = [
    ("thing/product/+/osd", 0),
    ("thing/product/+/events", 0)
]
DURATION = 60  # Listen for 60 seconds

# The Master Dictionary that will hold every unique field we see
master_schema = {}
message_count = 0

def deep_merge(source, destination):
    """
    Recursively merges source dict into destination dict.
    If a key exists in both, it merges them.
    This allows us to build a complete schema from partial packets.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # If the node is a dict, recurse
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        elif isinstance(value, list):
            # If it's a list, we just keep the latest sample for schema purposes
            # (Merging lists of objects is complex, this is a schema approximation)
            destination[key] = value
        else:
            # It's a value (int, float, string), just update it (latest sample)
            destination[key] = value
    return destination

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker. Sniffing for {DURATION} seconds...")
        client.subscribe(TOPICS)
    else:
        print(f"❌ Connection Failed. Code: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    global master_schema, message_count
    try:
        payload = json.loads(msg.payload.decode())
        
        # Merge this packet into our Master Schema
        deep_merge(payload, master_schema)
        
        message_count += 1
        sys.stdout.write(f"\r📡 Captured Packet #{message_count} | Topic: {msg.topic}")
        sys.stdout.flush()
        
    except json.JSONDecodeError:
        pass # Ignore non-JSON messages
    except Exception as e:
        print(f"\n[!] Error: {e}")

# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure docs folder exists
    if not os.path.exists("docs"):
        os.makedirs("docs")

    client = mqtt.Client("SchemaSniffer")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("🚀 STARTING RAW DATA CAPTURE...")
        print("⚠️  PLEASE POWER ON THE DRONE NOW for best results!")
        
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        
        # Countdown
        start_time = time.time()
        while (time.time() - start_time) < DURATION:
            time.sleep(0.1)
            
        client.loop_stop()
        print("\n\n✅ Capture Complete.")
        
        # Save to file
        output_path = "docs/autel_raw_schema.json"
        with open(output_path, "w") as f:
            json.dump(master_schema, f, indent=4, sort_keys=True)
            
        print(f"📄 Raw Schema saved to: {output_path}")
        print("   (You can now open this file to see the full nested structure)")

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
        client.loop_stop()
