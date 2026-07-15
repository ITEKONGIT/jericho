# Mobile Application Assessment

This directory is the home for the tools we use to break down Android and iOS applications. As we often say, "The truth is hidden in the runtime," and these scripts are designed to expose what the developers try to keep under the hood.

## Network Interception
- **network/persist_proxy.sh**: This script uses ADB and iptables to force all device traffic through our intercepting proxy. It is particularly useful for those applications that ignore system-level proxy settings or use custom networking stacks. Just remember that it requires a rooted device or a permissive emulator to function.

## Runtime Instrumentation (Frida)
I maintain these scripts here to help with common bypasses and monitoring. I plan to add more bypasses here as I encounter new protections in the field.

- **frida/universal_android_bypass.js**: A centralized script for hooking common SSL pinning implementations and anti-tamper checks on Android.
- **frida/native_socket_monitor.js**: This hooks low-level socket APIs, allowing us to monitor data in transit before it gets encrypted or after it's been decrypted. It's a lifesaver when you need to identify hidden backend communication.

## A Note on Usage
Most of these tools require a bridged connection between your workstation and the target device, along with a running frida-server. Always double-check the target app's architecture (ARM/x86) before you start injecting hooks—it saves a lot of headaches.
