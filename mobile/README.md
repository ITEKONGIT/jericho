# Mobile Application Assessment

This directory is the home for the tools we use to break down Android and iOS applications. As we often say, "The truth is hidden in the runtime," and these scripts are designed to expose what the developers try to keep under the hood.

## Newcomer ramp

**What this field is.** A mobile app is a frontend whose backend logic I can watch from the *inside* — the runtime. Instead of guessing at API behavior through a proxy, I hook the running process and read (or change) what the app does: what it verifies, what it trusts, what it sends. Frida is the tool for that; the scripts here are pre-built hooks for the protections apps raise against being watched.

**Why people miss findings here.** Two failure modes read as dead ends but are actually signals. An empty proxy doesn't mean "no traffic" — it means the app dodged the proxy (custom stack, ignoring system settings); force it through with `network/persist_proxy.sh`. A bypass that loads without errors doesn't mean pinning is beaten — the pinning may live in native code, below the Java layer every standard hook touches. The recurring miss: **reading tool silence as a result instead of as a wrong-layer or wrong-tool signal.**

**Read order.** [`network/persist_proxy.sh`](network/persist_proxy.sh) first (get the traffic flowing), then [`ssl-pinning/universal_bypass.js`](ssl-pinning/universal_bypass.js) — the minimal single-purpose hook, which is what I want on an unknown target. Escalate to [`frida/universal_android_bypass.js`](frida/universal_android_bypass.js) (the heavy multi-hook script) only when the minimal one survives. When *that* stops working, [`docs/methodology/mobile-reversing.md`](../docs/methodology/mobile-reversing.md) is the escalation path — native-layer pinning and telemetry analysis. **Defer:** `native_socket_monitor.js` until the app turns out to speak a custom protocol over raw sockets.

## Network Interception

- **network/persist_proxy.sh**: This script uses ADB and iptables to force all device traffic through our intercepting proxy. It is particularly useful for those applications that ignore system-level proxy settings or use custom networking stacks. Just remember that it requires a rooted device or a permissive emulator to function.

## Runtime Instrumentation (Frida)

I maintain these scripts here to help with common bypasses and monitoring. I plan to add more bypasses here as I encounter new protections in the field.

- **frida/universal_android_bypass.js**: A centralized script for hooking common SSL pinning implementations and anti-tamper checks on Android.
- **frida/native_socket_monitor.js**: This hooks low-level socket APIs, allowing us to monitor data in transit before it gets encrypted or after it's been decrypted. It's a lifesaver when you need to identify hidden backend communication.

## SSL Pinning Bypass

- **ssl-pinning/universal_bypass.js**: A minimal, universal hook against `com.android.org.conscrypt.TrustManagerImpl.verifyChain` that returns the certificate chain unverified. Where `frida/universal_android_bypass.js` bundles pinning with anti-tamper suppression and traffic logging, this one does nothing but defeat the trust manager — which is what I want on an unknown target, since fewer hooks means fewer crashes while you're still learning the app's shape.

For what to do when the app pins at the native layer and Java hooks are ignored, see **docs/methodology/mobile-reversing.md**.

## A Note on Usage

Most of these tools require a bridged connection between your workstation and the target device, along with a running frida-server. Always double-check the target app's architecture (ARM/x86) before you start injecting hooks—it saves a lot of headaches.
