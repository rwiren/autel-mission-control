"""
-----------------------------------------------------------------------------
Script Name: monitor_mqtt.py
Description: Real-time MQTT packet inspector. Subscribes to all topics (#)
             and pretty-prints incoming JSON telemetry for verification.
Version:     1.0.0
Author:      System Architect
Date:        2025-12-14
-----------------------------------------------------------------------------
"""

import paho.mqtt.client as mqtt
import json
import sys
from datetime import datetime

# Configuration
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
TOPIC_FILTER = "#"  # Wildcard to catch ALL messages

# ANSI Colors for readability
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    if rc == 0:
        print(f"{Colors.GREEN}[MQTT] ✅ Connected to Broker at {BROKER_ADDRESS}:{BROKER_PORT}{Colors.ENDC}")
        print(f"{Colors.BLUE}[MQTT] 📡 Subscribing to topic: '{TOPIC_FILTER}'{Colors.ENDC}")
        print(f"{Colors.HEADER}[SYSTEM] Waiting for incoming telemetry... (Ctrl+C to exit){Colors.ENDC}\n")
        client.subscribe(TOPIC_FILTER)
    else:
        print(f"{Colors.FAIL}[MQTT] ❌ Connection failed with code {rc}{Colors.ENDC}")
        sys.exit(1)

def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    try:
        # Try to decode payload as JSON for pretty printing
        payload_str = msg.payload.decode('utf-8')
        payload_json = json.loads(payload_str)
        formatted_json = json.dumps(payload_json, indent=2)
        
        print(f"{Colors.YELLOW}[{timestamp}] 📬 {msg.topic}{Colors.ENDC}")
        print(f"{formatted_json}")
        print("-" * 40)
        
    except json.JSONDecodeError:
        # Fallback for raw strings/binary
        print(f"{Colors.YELLOW}[{timestamp}] 📝 {msg.topic} (Raw):{Colors.ENDC} {msg.payload}")
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR] Could not decode message: {e}{Colors.ENDC}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n{Colors.HEADER}[SYSTEM] Monitor stopped by user.{Colors.ENDC}")
        client.disconnect()
    except ConnectionRefusedError:
        print(f"{Colors.FAIL}[ERROR] Connection refused. Is the Docker container 'autel_broker' running?{Colors.ENDC}")

if __name__ == "__main__":
    main()
