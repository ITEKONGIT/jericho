# DOCUMENTATION & CHECKLISTS

Standardized assessment methodologies and operational security checklists — the "why" behind the techniques, kept next to the tooling that implements them.

## Methodology

- **methodology/frontend-encryption.md** — Frontend Encryption Analysis. Where client-side crypto actually breaks down: key derivation (KDFs, salts, iteration counts), the developer's own encryption lifecycle, and a trace workflow that starts from the JavaScript bundle rather than from the cipher name.
- **methodology/mobile-reversing.md** — Hardened SSL Pinning & Obfuscation Analysis. What to do when automated interception fails: telemetry capture and protocol analysis, port normalization for backends that dodge 443/80, and native-layer pinning that Java-level Frida hooks will not touch.

## Checklists

- **Infra-Security-Assessment-Checklist.md** — Infrastructure Security Assessment Checklist (DigitalOcean / Hetzner focus). Pre-engagement and authorization gates, external cloud attack-surface enumeration, host-level misconfiguration auditing with expected vulnerable/hardened output per check, cloud config review, and the caveats for running the host checks as a least-privileged account.
