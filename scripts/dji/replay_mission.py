#!/usr/bin/env python3
"""
-----------------------------------------------------------------------------
Script Name: replay_mission.py
Description: Replays a sample DJI mission dataset into InfluxDB in a
             continuous loop for dashboard testing and UI validation.
             Uses the DJI Cloud API field naming convention
             (see docs/DJI_DATA_SCHEMA.md).

             Includes one intentional "bad packet" (0,0 coordinates) to
             validate that your Grafana filters and Flux queries reject it.
Version:     1.0.0
Author:      RW
Date:        2026-04-05
-----------------------------------------------------------------------------
Usage:
    python3 replay_mission.py
    # Sends 1 packet/second to InfluxDB in an infinite loop.
    # Press Ctrl+C to stop.

Configuration:
    Set INFLUX_TOKEN via environment variable:
        export INFLUX_TOKEN="your-token-here"

Dependencies:
    pip install influxdb-client
-----------------------------------------------------------------------------
"""

import os
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
INFLUX_URL    = "http://localhost:8086"
INFLUX_ORG    = "dji_ops"
INFLUX_BUCKET = "drone_telemetry"

# Read token from environment variable; fall back to placeholder for dev.
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-super-secret-token-change-me")

# ---------------------------------------------------------------------------
# SAMPLE MISSION DATA
# DJI field names mirror docs/DJI_DATA_SCHEMA.md.
# Coordinates are fictional — replace with a real flight path for training.
# ---------------------------------------------------------------------------
mission_data = [
    # Normal climb-out sequence
    {"latitude": 60.319473, "longitude": 24.830822, "height": 5.0,   "elevation": 138.0, "rtk_state": 3, "horizontal_speed": 0.2},
    {"latitude": 60.319480, "longitude": 24.830815, "height": 15.0,  "elevation": 148.0, "rtk_state": 3, "horizontal_speed": 1.5},
    {"latitude": 60.319490, "longitude": 24.830800, "height": 30.0,  "elevation": 163.0, "rtk_state": 3, "horizontal_speed": 3.0},
    {"latitude": 60.319510, "longitude": 24.830775, "height": 50.0,  "elevation": 183.0, "rtk_state": 3, "horizontal_speed": 5.0},
    {"latitude": 60.319540, "longitude": 24.830740, "height": 50.2,  "elevation": 183.2, "rtk_state": 3, "horizontal_speed": 8.0},
    # Intentional bad packet — tests Grafana null / zero-coordinate filtering
    {"latitude": 0.0,       "longitude": 0.0,       "height": 0.0,   "elevation": 0.0,   "rtk_state": 0, "horizontal_speed": 0.0},
    # Cruise phase
    {"latitude": 60.319580, "longitude": 24.830700, "height": 50.1,  "elevation": 183.1, "rtk_state": 3, "horizontal_speed": 7.5},
    {"latitude": 60.319620, "longitude": 24.830660, "height": 49.9,  "elevation": 182.9, "rtk_state": 2, "horizontal_speed": 7.0},
    # Descent
    {"latitude": 60.319650, "longitude": 24.830630, "height": 30.0,  "elevation": 163.0, "rtk_state": 3, "horizontal_speed": 3.5},
    {"latitude": 60.319670, "longitude": 24.830615, "height": 10.0,  "elevation": 143.0, "rtk_state": 3, "horizontal_speed": 1.0},
    {"latitude": 60.319680, "longitude": 24.830610, "height": 0.5,   "elevation": 133.5, "rtk_state": 3, "horizontal_speed": 0.1},
]

# ---------------------------------------------------------------------------
# REPLAY LOOP
# ---------------------------------------------------------------------------

def replay():
    client    = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(f"🚀 DJI MISSION REPLAY v1.0.0")
    print(f"   Bucket : {INFLUX_BUCKET} @ {INFLUX_URL}")
    print(f"   Packets: {len(mission_data)} per loop (1 packet/second)")
    print("   Press Ctrl+C to stop.\n")

    loop = 0
    while True:
        loop += 1
        print(f"📍 Loop #{loop} — replaying {len(mission_data)} packets...")

        for packet in mission_data:
            # Build an InfluxDB point using DJI Cloud API field names.
            # Measurement "mqtt_consumer" matches the Telegraf MQTT consumer
            # output format so these points are compatible with production dashboards.
            point = (
                Point("mqtt_consumer")
                .field("latitude",         packet["latitude"])
                .field("longitude",        packet["longitude"])
                .field("height",           packet["height"])
                .field("elevation",        packet["elevation"])
                .field("rtk_state",        packet["rtk_state"])
                .field("horizontal_speed", packet["horizontal_speed"])
                .time(time.time_ns(), WritePrecision.NS)
            )

            write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)

            if packet["latitude"] == 0.0:
                print(f"   ⚠️  Sent BAD packet (0.0, 0.0) — verify Grafana ignores it.")
            else:
                print(
                    f"   📡 alt={packet['height']:.1f}m  "
                    f"rtk_state={packet['rtk_state']}  "
                    f"speed={packet['horizontal_speed']:.1f}m/s"
                )

            time.sleep(1)

if __name__ == "__main__":
    try:
        replay()
    except KeyboardInterrupt:
        print("\n🛑 Replay stopped.")
