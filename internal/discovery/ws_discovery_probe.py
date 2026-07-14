import time
from wsdiscovery import WSDiscovery

# Initialize the WS-Discovery service
wsd = WSDiscovery()

print("[*] Starting WS-Discovery service...")
wsd.start()

print("[*] Broadcasting probe to local network (waiting 5 seconds)...")
# Search for all types of web services available on the network
services = wsd.searchServices()

print(f"[*] Found {len(services)} device(s):\n")

# Loop through and print out the details of found services
for service in services:
    print(f"--- Device Found ---")
    print(f"Types: {service.getTypes()}")
    print(f"Endpoints/XAddrs: {service.getXAddrs()}")
    print(f"Scopes: {service.getScopes()}")
    print("-" * 20 + "\n")

# Clean up and stop the background threads
wsd.stop()
