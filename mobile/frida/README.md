# Frida Instrumentation Tooling

Custom JavaScript hooks for dynamic mobile application analysis via Frida.

## Active Scripts

### `universal_android_bypass.js`
A heavy-duty anti-tamper bypass script. 
* Prevents the application from drawing error UI (Dialogs, Toasts, Popups).
* Blocks runtime self-termination (`System.exit`, `Activity.finish`).
* Bypasses standard OkHttp and X509TrustManager SSL Pinning.
* Hooks `RealCall.execute` to actively log HTTP traffic to the console.

### `native_socket_monitor.js`
A low-level hook targeting `libc`. It intercepts the `connect()` function to expose raw socket connections. Highly useful when an application ignores standard HTTP/S APIs and communicates over custom TCP/UDP protocols.
