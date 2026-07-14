#!/bin/bash

# Forceful Transparent Proxy for Android (via ADB)
# Routes all device HTTP/HTTPS traffic to a specified intercepting proxy (like Burp Suite).

if [ -z "$1" ]; then
    echo "Usage: $0 <BURP_IP>"
    echo "Example: $0 192.168.1.50"
    exit 1
fi

TARGET_BURP=$1

while true; do
    # Wait for the device to be available
    adb wait-for-device
    
    echo "[*] Device detected. Applying Transparent Proxy to $TARGET_BURP:8081..."
    
    # Enable IP Forwarding on host
    sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null

    # Flush and Redirect via iptables
    adb shell "su -c 'iptables -t nat -F'"
    adb shell "su -c 'iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination $TARGET_BURP:8081'"
    adb shell "su -c 'iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination $TARGET_BURP:8081'"
    adb shell "su -c 'iptables -t nat -A POSTROUTING -j MASQUERADE'"
    
    echo "[+] Rules applied. Waiting for next refresh..."
    sleep 10
done
