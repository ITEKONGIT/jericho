# INTERNAL: Utility & Post-Exploitation
Internal tools and complex external dependencies used for specialized assessments.

## Newcomer ramp

**What this field is.** The internal network is the space behind the perimeter — flat LANs, forgotten devices, hardware nobody models as computers. The tools here answer two questions: *what is actually on this network* (not what the scanner found), and *what can I do with the things everyone ignores*.

**Why people miss findings here.** Scans ask TCP/ICMP questions and treat silence as an answer — whole device classes (printers, cameras, IoT) answer UDP multicast instead, so a clean scan is not a clean network. And inventoried-but-unmodeled devices get no patching and no threat model; a printer is a host with a filesystem, memory, and stored credentials that nobody thinks to audit. The recurring miss: **trusting the scanner's silence as a result.**

**Read order.** [`discovery/`](discovery/) first — establish what's really there. Then [`printers/`](printers/) if anything printer-ish answered; the vendored PRET README explains its scope and the Python 2 caveat before you run anything. **Defer:** everything until you actually have LAN access — this module is useless from outside and trivial once inside.

- **discovery/**: Custom network reconnaissance and service discovery tools.
- **printers/**: Contains PRET (Printer Exploitation Toolkit) and associated MIB/PJL/PCL resources for firmware analysis.
