#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: flight_recorder.py
Description: Records all incoming Autel MQTT telemetry to a timestamped
             JSONL log file for offline analysis and replay.
             Subscribes to 'thing/product/+/osd' (Autel Cloud API OSD topic).
Version:     1.1.0
Author:      RW
Date:        2025-12-14
-----------------------------------------------------------------------------
Usage:
    python3 flight_recorder.py
    # Output: flight_logs/flight_YYYYMMDD_HHMMSS.jsonl

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
BROKER_ADDRESS  = "localhost"
BROKER_PORT     = 1883
SUBSCRIBE_TOPIC = "thing/product/+/osd"  # Autel Cloud API telemetry topic
LOG_DIR         = "flight_logs"

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
    """Subscribe to the Autel OSD topic once the connection is established."""
    client.subscribe(SUBSCRIBE_TOPIC)

def on_message(client, userdata, msg):
    """Append each received message to the JSONL log file."""
    with open(filename, "a") as f:
        # Format: ISO timestamp | MQTT topic | raw JSON payload
        f.write(f"{datetime.datetime.now().isoformat()} | {msg.topic} | {msg.payload.decode('utf-8', errors='replace')}\n")
    print(".", end="", flush=True)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
client = mqtt.Client(client_id="FlightRecorder", protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

print(f"🔴 RECORDER STARTED: Saving to {filename}")
client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)
client.loop_forever()
