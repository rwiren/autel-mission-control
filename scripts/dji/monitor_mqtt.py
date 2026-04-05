#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: monitor_mqtt.py
Description: Real-time DJI Cloud API MQTT packet inspector. Subscribes to
             all topics (#) and pretty-prints incoming JSON telemetry for
             live verification during drone operations.
Version:     1.0.0
Author:      RW
Date:        2026-04-05
-----------------------------------------------------------------------------
Usage:
    python3 monitor_mqtt.py
    # Press Ctrl+C to exit

DJI Key Topics:
    thing/product/{sn}/osd          — Aircraft state (telemetry)
    thing/product/{sn}/events       — Events (RTH trigger, battery warn, etc.)
    thing/product/{sn}/requests     — Commands sent to the aircraft
    sys/product/{sn}/status         — Dock / RC heartbeat

Dependencies:
    pip install paho-mqtt
-----------------------------------------------------------------------------
"""

import paho.mqtt.client as mqtt
import json
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
BROKER_ADDRESS = "localhost"
BROKER_PORT    = 1883
TOPIC_FILTER   = "#"  # Wildcard — capture every topic

# ---------------------------------------------------------------------------
# ANSI COLOR CODES
# ---------------------------------------------------------------------------

class Colors:
    HEADER = '\033[95m'
    BLUE   = '\033[94m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    FAIL   = '\033[91m'
    ENDC   = '\033[0m'
    BOLD   = '\033[1m'

# ---------------------------------------------------------------------------
# MQTT CALLBACKS
# ---------------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    """Subscribe to all topics once connected."""
    if rc == 0:
        print(f"{Colors.GREEN}[MQTT] ✅ Connected to DJI Broker at {BROKER_ADDRESS}:{BROKER_PORT}{Colors.ENDC}")
        print(f"{Colors.BLUE}[MQTT] 📡 Subscribing to topic: '{TOPIC_FILTER}'{Colors.ENDC}")
        print(f"{Colors.HEADER}[SYSTEM] Waiting for DJI telemetry... (Ctrl+C to exit){Colors.ENDC}\n")
        client.subscribe(TOPIC_FILTER)
    else:
        print(f"{Colors.FAIL}[MQTT] ❌ Connection failed — code {rc}{Colors.ENDC}")
        sys.exit(1)

def on_message(client, userdata, msg):
    """Pretty-print each incoming message with a timestamp."""
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    try:
        # Attempt JSON decode for pretty output
        payload_str  = msg.payload.decode('utf-8')
        payload_json = json.loads(payload_str)
        formatted    = json.dumps(payload_json, indent=2)

        print(f"{Colors.YELLOW}[{timestamp}] 📬 {msg.topic}{Colors.ENDC}")
        print(formatted)
        print("-" * 40)

    except json.JSONDecodeError:
        # Raw / binary payload fallback
        print(f"{Colors.YELLOW}[{timestamp}] 📝 {msg.topic} (Raw):{Colors.ENDC} {msg.payload}")
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Could not decode message: {e}{Colors.ENDC}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    client = mqtt.Client(client_id="DJI_MQTTMonitor_v1.0", protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n{Colors.HEADER}[SYSTEM] Monitor stopped by user.{Colors.ENDC}")
        client.disconnect()
    except ConnectionRefusedError:
        print(f"{Colors.FAIL}[ERROR] Connection refused. Is the MQTT broker running?{Colors.ENDC}")

if __name__ == "__main__":
    main()
