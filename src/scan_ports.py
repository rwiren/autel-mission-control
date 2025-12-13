import socket

# Configuration
TARGET_IP = "192.168.1.201"
PORTS_TO_CHECK = [554, 8554, 1935]

print(f"🕵️  Scanning Autel Controller ({TARGET_IP})...")
print("-" * 40)

for port in PORTS_TO_CHECK:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0) # 1 second timeout
    result = sock.connect_ex((TARGET_IP, port))
    
    status = "✅ OPEN" if result == 0 else "❌ CLOSED"
    print(f"Port {port}: {status}")
    sock.close()

print("-" * 40)
print("Scan complete.")
