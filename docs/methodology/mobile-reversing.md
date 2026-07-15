# Methodology: Hardened SSL Pinning & Obfuscation Analysis

## 1. The Obfuscation-Pinning Synergy
Developers often combine **Native Obfuscation** (non-standard ports like 1443) with **Runtime Pinning** (`TrustManagerImpl`). The goal is to make the app "invisible" to standard `iptables` redirection at 443/80.

## 2. The Investigative Chain
When automated tools fail to intercept traffic:
1. **Telemetry Capture:** Use `tcpdump` to capture raw binary blobs.
2. **Protocol Analysis:** Use `scapy` to filter and map the capture. Look for traffic patterns that do not originate from port 443.
3. **Port Normalization:** Update `iptables` rules to match the *observed* backend port (e.g., 1443).
4. **Runtime Instrumentation:** Inject into `com.android.org.conscrypt.TrustManagerImpl` to neutralize the certificate chain verification.

## 3. Advanced Persistence (The "Future Vector")
If the app implements native-level C++ pinning (e.g., via `libhermes.so` or `libssl.so`), Frida Java hooks will be ignored.
* **Vector:** Binary patching or `Stalker` (Frida's instruction-level tracer) is required to find the `SSL_read` / `SSL_write` hooks at the native layer.
