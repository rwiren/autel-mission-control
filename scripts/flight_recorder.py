import paho.mqtt.client as mqtt
import datetime
import os

# CONFIG
LOG_DIR = "flight_logs"
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
filename = f"{LOG_DIR}/flight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

def on_message(client, userdata, msg):
    with open(filename, "a") as f:
        # Save timestamp + topic + payload
        f.write(f"{datetime.datetime.now().isoformat()} | {msg.topic} | {msg.payload.decode()}\n")
    print(f".", end="", flush=True)

client = mqtt.Client("FlightRecorder")
client.on_connect = lambda c, u, f, rc: c.subscribe("thing/product/+/osd")
client.on_message = on_message

print(f"🔴 RECORDER STARTED: Saving to {filename}")
client.connect("localhost", 1883, 60)
client.loop_forever()
