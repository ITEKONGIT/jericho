# Internal Host Assessments & Hardening

This directory contains scripts utilized for internal security assessments, focusing on host-level enumeration, baseline compliance, and server hardening verification. 

The tooling is designed to evaluate environments—particularly cloud-native VPS deployments like DigitalOcean—against established operational security standards.

## Active Tooling

### 1. Linux Host Security Auditor (`linux-host-audit.sh`)
A comprehensive, automated bash utility for assessing the security posture of a target Linux host. It is specifically tuned to identify common misconfigurations, missing defensive controls, and potential privilege escalation vectors.

**Cloud-Native & DigitalOcean Focus:**
* **Metadata SSRF Checks:** Verifies if the DigitalOcean metadata service (`169.254.169.254`) is exposed to the local VM, assessing the risk of Server-Side Request Forgery (SSRF) abuse.
* **Containerization Security:** Audits Docker configurations to identify if the daemon is running with default, unrestricted root privileges.

**Core Hardening Standards Assessed:**
* **Access & Authentication:** Validates SSH daemon hardening (`PermitRootLogin`, `MaxAuthTries`, `X11Forwarding`) and enumerates risky passwordless `sudo` entries (`NOPASSWD: ALL`).
* **Intrusion Prevention & Logging:** Verifies the active deployment of `fail2ban` and the `auditd` framework.
* **File System Security:** Audits mount point restrictions (`noexec`, `nosuid`, `nodev`) and scans for world-writable files across the host.
* **System Integrity:** Identifies pending critical security updates, required reboots, and the operational status of AppArmor.

**Usage:**
Execution requires root privileges for complete filesystem and service enumeration.
```bash
chmod +x linux-host-audit.sh
sudo ./linux-host-audit.sh
Note: Subsequent enumeration and assessment scripts will be documented here as they are added to the arsenal.
