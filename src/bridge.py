"""
-----------------------------------------------------------------------------
Script Name: bridge.py
Description: Core Telemetry Bridge for Autel Max 4T.
             Intercepts UDP broadcast packets, decodes binary/JSON structures,
             Normalizes data into a standard schema, and publishes to MQTT.
Version:     1.2.0 (Fix: Added RTK FIX status handling)
Author:      RW
Date:        2025-12-17
-----------------------------------------------------------------------------
"""

import socket
import json
import time
import logging
import os
import signal
import sys
from datetime import datetime
import paho.mqtt.client as mqtt

# --- Configuration ---
# Load from Environment or use Defaults
UDP_IP = "0.0.0.0"
UDP_PORT = 12000  # Standard Autel broadcast port
MQTT_BROKER = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_ROOT = "autel"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [BRIDGE] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TelemetryBridge:
    def __init__(self):
        self.running = True
        self.mqtt_client = None
        self.udp_sock = None
        
        # Graceful Shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle shutdown signals cleanly."""
        logger.info("🛑 Shutdown signal received. Stopping loop...")
        self.running = False

    def connect_mqtt(self):
        """Establish connection to the MQTT Broker."""
        try:
            self.mqtt_client = mqtt.Client(client_id="autel_bridge_v1.2", protocol=mqtt.MQTTv311)
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            logger.info(f"✅ MQTT Connected: {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            logger.error(f"🔴 MQTT Connection Failed: {e}")
            sys.exit(1)

    def setup_udp(self):
        """Bind to the UDP port to listen for drone broadcasts."""
        try:
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.bind((UDP_IP, UDP_PORT))
            # CRITICAL FIX: Set timeout so the loop can check self.running
            self.udp_sock.settimeout(1.0) 
            logger.info(f"📡 Listening for UDP Telemetry on port {UDP_PORT}")
        except Exception as e:
            logger.error(f"🔴 UDP Bind Failed: {e}")
            sys.exit(1)

    def _normalize_payload(self, raw_data):
        """
        CRITICAL: Takes messy, vendor-specific JSON and converts it 
        into a clean, standardized format for the database.
        """
        normalized = {}
        
        # Extract Timestamp
        normalized['timestamp'] = raw_data.get('timestamp', int(time.time() * 1000))
        
        # --- PATH A: DATA FROM DRONE ---
        if 'data' in raw_data and 'battery' in raw_data['data']:
            data = raw_data['data']
            normalized['device_type'] = 'drone'
            normalized['serial'] = raw_data.get('gateway', 'unknown_drone')
            
            normalized['batt'] = float(data.get('battery', {}).get('capacity_percent', 0))
            normalized['lat'] = round(float(data.get('latitude', 0)), 6)
            normalized['lon'] = round(float(data.get('longitude', 0)), 6)
            normalized['alt'] = round(float(data.get('height', 0)), 2)
            
            # --- RTK STATUS LOGIC ---
            pos = data.get('position_state', {})
            normalized['sat_count'] = int(pos.get('gps_number', 0))
            
            rtk_val = pos.get('rtk_inpos', 0)
            if rtk_val == 2:
                normalized['rtk_status'] = "FIX"    # High Precision (CM level)
            elif rtk_val == 1:
                normalized['rtk_status'] = "FLOAT"  # Medium Precision
            else:
                normalized['rtk_status'] = "NONE"   # Standard GPS

            normalized['heading'] = round(float(data.get('attitude_head', 0)), 2)

        # --- PATH B: DATA FROM CONTROLLER ---
        elif 'data' in raw_data and 'device_list' in raw_data['data']:
            data = raw_data['data']
            normalized['device_type'] = 'controller'
            normalized['serial'] = raw_data.get('gateway', 'unknown_controller')
            
            normalized['batt'] = float(data.get('capacity_percent', 0))
            normalized['lat'] = 0.0
            normalized['lon'] = 0.0
            normalized['alt'] = 0.0
            normalized['sat_count'] = 0
            normalized['heading'] = 0.0
            normalized['rtk_status'] = "NONE"

        else:
            return None 

        return normalized

    def run(self):
        """Main Loop: Receive -> Decode -> Normalize -> Publish"""
        self.connect_mqtt()
        self.setup_udp()

        buffer_size = 65535 

        while self.running:
            try:
                # 1. Receive Packet (With Timeout)
                try:
                    data, addr = self.udp_sock.recvfrom(buffer_size)
                except socket.timeout:
                    # Timeout reached, loop back to check self.running
                    continue
                
                # 2. Decode
                try:
                    decoded_str = data.decode('utf-8')
                    json_data = json.loads(decoded_str)
                except json.JSONDecodeError:
                    continue

                # 3. Publish RAW
                sn = json_data.get('gateway', 'unknown')
                raw_topic = f"thing/product/{sn}/osd"
                self.mqtt_client.publish(raw_topic, decoded_str)

                # 4. Publish NORMALIZED
                clean_data = self._normalize_payload(json_data)
                if clean_data:
                    clean_topic = "telemetry/normalized"
                    self.mqtt_client.publish(clean_topic, json.dumps(clean_data))
                    
                    if int(time.time()) % 5 == 0: 
                        logger.debug(f"Processed packet for {clean_data['device_type']}")

            except socket.error as e:
                logger.error(f"Socket Error: {e}")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                
        # Cleanup
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        if self.udp_sock:
            self.udp_sock.close()
        logger.info("👋 Bridge Stopped.")

if __name__ == "__main__":
    bridge = TelemetryBridge()
    bridge.run()
