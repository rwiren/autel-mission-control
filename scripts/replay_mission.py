import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# CONFIGURATION
TOKEN = "my-super-secret-token-change-me"
ORG = "autel_ops"
BUCKET = "telemetry"
URL = "http://localhost:8086"

# Extracted from your log dump (Cleaned)
mission_data = [
    {"lat": 60.319473, "lon": 24.830822, "alt": 131.2, "sats": 5},
    {"lat": 60.319473, "lon": 24.830818, "alt": 131.5, "sats": 4},
    {"lat": 60.319473, "lon": 24.830818, "alt": 131.7, "sats": 5},
    # Intentionally inserting a "Bad Packet" to test your filters
    {"lat": 0.0, "lon": 0.0, "alt": 0.0, "sats": 0}, 
    {"lat": 60.319477, "lon": 24.830830, "alt": 130.8, "sats": 3},
    {"lat": 60.319477, "lon": 24.830828, "alt": 130.8, "sats": 3},
    {"lat": 60.319477, "lon": 24.830830, "alt": 130.8, "sats": 4},
]

def replay():
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    print(f"🚀 Replaying {len(mission_data)} packets to InfluxDB...")

    while True:
        for packet in mission_data:
            # We assume Telegraf format: measurement="mqtt_consumer", fields="data_..."
            point = Point("mqtt_consumer") \
                .field("data_latitude", packet["lat"]) \
                .field("data_longitude", packet["lon"]) \
                .field("data_height", packet["alt"]) \
                .field("data_gps_sats", packet["sats"]) \
                .time(time.time_ns(), WritePrecision.NS)
            
            write_api.write(BUCKET, ORG, point)
            
            if packet["lat"] == 0.0:
                print("   ⚠️  Sent BAD packet (0.0, 0.0) - Check if Grafana ignores this!")
            else:
                print(f"   📡 Sent GOOD packet: {packet['lat']}, {packet['lon']}")
            
            time.sleep(1) # Send one packet per second

if __name__ == "__main__":
    try:
        replay()
    except KeyboardInterrupt:
        print("\n🛑 Replay stopped.")
