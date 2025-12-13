"""
================================================================================
SCRIPT: src/bridge.py
DESCRIPTION: 
    Production Bridge v2.3.0.
    Connects to MQTT, parses Autel Max 4T Telemetry, and ingests data into InfluxDB.
    
    NEW IN v2.3.0: 
    - Extracts 'pos_type' (RTK Status).
    - Maps integer codes to Human Readable statuses (FIX, FLOAT, SINGLE).
    - Adds GPS Satellite count (if available).

AUTHOR: System Architect
DATE: 2025-12-13
VERSION: 2.3.0 (RTK Support Added)
================================================================================
"""

import os
import json
import logging
import sys
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# --- CONFIG ---
CONFIG = {
    "MQTT_BROKER": os.getenv("MQTT_BROKER_HOST", "localhost"),
    "MQTT_PORT": int(os.getenv("MQTT_PORT", 1883)),
    "MQTT_TOPIC": "thing/product/+/osd",
    "INFLUX_URL": os.getenv("INFLUX_URL", "http://localhost:8086"),
    "INFLUX_TOKEN": os.getenv("INFLUX_TOKEN"),
    "INFLUX_ORG": os.getenv("INFLUX_ORG"),
    "INFLUX_BUCKET": os.getenv("INFLUX_BUCKET")
}

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BRIDGE] - %(levelname)s - %(message)s')
logger = logging.getLogger()

if not CONFIG["INFLUX_TOKEN"]:
    logger.critical("❌ Missing INFLUX_TOKEN in .env file.")
    sys.exit(1)

# --- DATABASE ---
try:
    influx_client = InfluxDBClient(
        url=CONFIG["INFLUX_URL"], token=CONFIG["INFLUX_TOKEN"], org=CONFIG["INFLUX_ORG"]
    )
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    logger.info(f"✅ Database Connected: {CONFIG['INFLUX_URL']}")
except Exception as e:
    logger.critical(f"❌ Database Error: {e}")
    sys.exit(1)

# --- RTK MAPPING HELPER ---
def get_rtk_status_label(pos_type):
    """
    Maps Autel pos_type integers to readable labels.
    Based on standard Autel/MAVLink definitions.
    """
    try:
        pt = int(pos_type)
        if pt == 0: return "NONE"
        if pt == 16: return "SINGLE"     # Standard GPS (Accuracy ~2-5m)
        if pt == 34: return "RTK_FLOAT"  # RTK Converging (Accuracy ~0.5m)
        if pt == 50: return "RTK_FIX"    # RTK Locked (Accuracy ~0.02m)
        return f"UNKNOWN_{pt}"
    except:
        return "ERROR"

# --- PROCESSOR ---
def process_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        data = payload.get("data", {})
        
        # Topic: thing/product/{SN}/osd
        try: sn = msg.topic.split('/')[2]
        except: sn = "unknown"

        # Safe Extraction of Standard Telemetry
        lat = float(data.get("latitude", 0.0))
        lon = float(data.get("longitude", 0.0))
        alt = float(data.get("height", 0.0))
        heading = float(data.get("attitude_head", 0.0))
        
        # --- NEW: RTK / GNSS EXTRACTION ---
        pos_type = int(data.get("pos_type", 0))
        rtk_label = get_rtk_status_label(pos_type)
        
        # Some Autel firmwares put sat count in nested 'gps' or top level 'gps_count'
        # We default to 0 if not found
        sats = int(data.get("gps_count", data.get("satellite_count", 0)))

        # Battery
        batt_raw = data.get("battery", {})
        batt = float(batt_raw.get("capacity_percent", 0)) if isinstance(batt_raw, dict) else 0.0

        # Construct Point with RTK Tags
        p = Point("telemetry") \
            .tag("drone_sn", sn) \
            .tag("rtk_status", rtk_label) \
            .field("lat", lat).field("lon", lon) \
            .field("alt", alt).field("heading", heading) \
            .field("batt", batt) \
            .field("pos_type_raw", pos_type) \
            .field("sat_count", sats)

        write_api.write(bucket=CONFIG["INFLUX_BUCKET"], record=p)
        
        # Debug Log for RTK (Optional)
        # if pos_type > 0:
        #    logger.info(f"RTK UPDATE | Status: {rtk_label} ({pos_type}) | Sats: {sats}")

    except Exception as e:
        logger.warning(f"Parse Error: {e}")

# --- MAIN ---
def main():
    client = mqtt.Client(client_id="Autel_Bridge_v2")
    client.on_message = process_message

    while True:
        try:
            logger.info(f"🔌 Connecting to Broker ({CONFIG['MQTT_BROKER']})...")
            client.connect(CONFIG['MQTT_BROKER'], CONFIG['MQTT_PORT'], 60)
            client.subscribe(CONFIG['MQTT_TOPIC'])
            logger.info("🟢 Bridge Active.")
            client.loop_forever()
        except Exception as e:
            logger.error(f"🔴 Connection Failed: {e}. Retry 5s...")
            time.sleep(5)

if __name__ == "__main__":
    main()
