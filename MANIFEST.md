# Jericho: Repository Manifest

This document serves as the master guide to the functional components of the Jericho arsenal.

## 1. BaaS (Backend-as-a-Service)
* **Purpose:** Methodology for auditing modern cloud-native database architectures.
* **Problems Solved:** Identifying misconfigured access rules in JSON-based database structures and preventing unauthorized data extraction.
* **Content:** Contains deep-dives into Firebase and Supabase security rules and API enumeration strategies.

## 2. Cloud-Enum (Cloud Infrastructure)
* **Purpose:** Methodologies for cloud environment assessment and privilege escalation.
* **Problems Solved:** Automates the transition from initial access to full project takeover in AWS, GCP, and Azure.
* **Content:** Contains scripts for console federation (AWS), metadata service abuse (GCP), and Service Principal/Managed Identity exploitation (Azure), plus Linux host hardening tooling under `Host-Audit/`.

## 3. Internal (Network & Hardware)
* **Purpose:** Internal reconnaissance and peripheral asset exploitation.
* **Problems Solved:** Discovers hidden network assets that standard scans miss and provides interactive exploitation interfaces for printer and network hardware.
* **Content:** WS-Discovery probing tools and the PRET interface framework.

## 4. Mobile (Instrumentation & Proxy)
* **Purpose:** Dynamic mobile application analysis and traffic interception.
* **Problems Solved:** Bypasses application-level proxy detection and anti-tamper mechanisms (SSL pinning, root detection).
* **Content:** Includes transparent proxy enforcement scripts and universal Frida bypass templates.

## 5. Web-App (Intruder Utilities)
* **Purpose:** Application-layer stress testing and credential fuzzing.
* **Problems Solved:** Identifies weak authentication endpoints, password reset flaws, token confusion, source map leakage, Apache/.htaccess misconfiguration, cache invalidation bugs, and brute-force vulnerabilities.
* **Content:** Custom scripts for automated request mutation, credential testing, token/JWT review, password reset methodology, source map analysis, Apache configuration review, and read-only GraphQL endpoint/introspection enumeration.

## 6. Binary-Exploitation (Compiled Artifacts)
* **Purpose:** Methodology and tooling for auditing compiled programs directly — the ELF artifact as attack surface, rather than the service it exposes.
* **Problems Solved:** Provides a repeatable path from an unknown binary to a working exploit: fingerprinting the artifact, reading its active memory protections, locating memory corruption, and selecting the payload shape that fits. Removes the guesswork from offset calculation and protection interpretation.
* **Content:** A first-person working map covering the ten-stage workflow (fingerprint → protections → shortcuts → disassembly → vulnerability → shape → offset → payload → local → remote), a `shapes/` library of exploit patterns (ret2win and ret2shellcode solved; ret2libc, ROP, and format-string in progress), and `tools/find_offset.py` for static and dynamic offset discovery.

## 7. Exploits (Exploitation Suite)
* **Purpose:** Extensible library of validated exploit and CVE verification modules behind a single standard interface.
* **Problems Solved:** Turns one-off proof-of-concept scripts into configuration-agnostic modules with consistent output, so a finding can be reproduced and compared across engagements instead of rewritten each time.
* **Content:** Appsmith audit suite (information disclosure, account manipulation, and CVE-2024-55963 RCE) and the Azure Kudu SCM auditor (credential validation and automated environment secret extraction).

## 8. AI-Inference (Local LLM Bridge)
* **Purpose:** Keeps LLM-assisted offensive security work on-premise, so target details never leave the operator's own hardware.
* **Problems Solved:** Removes the data-leakage risk of sending target context to third-party inference APIs, and provides a CLI bridge from the test workstation into a locally hosted model server.
* **Content:** A Parrot OS agent script for driving the local inference API from an active shell, and a Windows host binder for exposing a local Ollama instance.

## 9. Documentation (Methodology & Checklists)
* **Purpose:** Centralized assessment methodology and operational security checklists.
* **Problems Solved:** Keeps the "why" next to the "how" — the reasoning behind a technique is what makes it reproducible on the next target, and what stops a checklist from being followed blindly.
* **Content:** Frontend encryption analysis and hardened SSL pinning / obfuscation methodology, plus infrastructure security assessment checklists.
