# Jericho: Repository Manifest

This document serves as the master guide to the functional components of the Jericho arsenal.

## 1. BaaS (Backend-as-a-Service)
* **Purpose:** Methodology for auditing modern cloud-native database architectures.
* **Problems Solved:** Identifying misconfigured access rules in JSON-based database structures and preventing unauthorized data extraction.
* **Content:** Contains deep-dives into Firebase and Supabase security rules and API enumeration strategies.

## 2. Cloud-Enum (Cloud Infrastructure)
* **Purpose:** Methodologies for cloud environment assessment and privilege escalation.
* **Problems Solved:** Automates the transition from initial access to full project takeover in AWS, GCP, and Azure.
* **Content:** Contains scripts for console federation (AWS), metadata service abuse (GCP), and Service Principal/Managed Identity exploitation (Azure).

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
* **Problems Solved:** Rapidly identifies weak authentication endpoints and validates brute-force vulnerabilities.
* **Content:** Custom scripts for automated request mutation, credential testing, and read-only GraphQL endpoint/introspection enumeration.
