# Jericho

And the walls came tumbling down.

A centralized repository for technical methodologies, utility scripts, and security-focused research.

## Repository Structure

* **/ai-inference/**: Local, on-premise LLM bridge for offensive-security workflows.
* **/baas/**: Backend-as-a-Service integration and configuration analysis.
* **/binary-exploitation/**: Auditing compiled programs directly — memory corruption and exploit construction.
* **/cloud-enum/**: Methodology and tooling for cloud-based environment assessment.
* **/docs/**: Assessment methodology and operational security checklists.
* **/exploits/**: Validated exploit and CVE verification modules behind a standard interface.
* **/internal/**: Local network discovery and utility scripts.
* **/mobile/**: Dynamic instrumentation and analysis configurations.
* **/web-app/**: Web-based utility tools for automation and testing.

## Where do I start? (routing by what's in front of me)

The structure above says what lives where. This says what to open when I'm standing in front of something real and can't remember which door it was behind.

| What's in front of me | Module | Open first |
|---|---|---|
| A compiled binary (ELF/PE), or a crashing service | [binary-exploitation/](binary-exploitation/) | the "What is a binary?" section below, then [`tools/triage.sh`](binary-exploitation/tools/triage.sh) |
| A web app and a browser | [web-app/](web-app/) | [`auth-endpoints/`](web-app/auth-endpoints/) — everything else in that module hangs off auth |
| A Supabase or Firebase URL (or a frontend bundle) | [baas/](baas/) | [`baas/README.md`](baas/README.md) — the assessment pipeline, then the arsenal |
| Cloud credentials, or a box inside AWS/GCP/Azure | [cloud-enum/](cloud-enum/) | [`docs/Infra-Security-Assessment-Checklist.md`](docs/Infra-Security-Assessment-Checklist.md), then [`Host-Audit/`](cloud-enum/Host-Audit/) |
| LAN access (or "the scan said the network is clean") | [internal/](internal/) | [`discovery/`](internal/discovery/) — sweeps miss whole classes of assets |
| An APK/IPA, or an app that refuses to proxy | [mobile/](mobile/) | [`network/persist_proxy.sh`](mobile/network/persist_proxy.sh), then the minimal pinning bypass |
| A known CVE or a named product (Appsmith, Kudu) | [exploits/](exploits/) | [`exploits/README.md`](exploits/README.md) for the interface, then the module |
| I want LLM help but the target can't leave my hardware | [ai-inference/](ai-inference/) | [`ai-inference/README.md`](ai-inference/README.md) |

**Methodology and checklists** (the "why" layer) live in [`docs/`](docs/). The cross-cutting index of bug classes people tend to never see is [`docs/classes-people-miss.md`](docs/classes-people-miss.md) — start there if the question is "what am I probably overlooking?" rather than "what is this file?"

Every module README now opens with the same three-part ramp: **what this field is** (for day one), **why people miss its findings** (the non-obvious part), and a **read order** (what to read now, what can wait). Skim the ramp, read in order, defer the rest until a target makes it relevant.

## What is a binary?

Everything else in this repository audits a running *service*. `binary-exploitation/` audits the compiled *program*.

A binary is the machine code the CPU executes directly — `ELF` on Linux, `PE` on Windows, `Mach-O` on macOS — produced when source is compiled and linked. It isn't readable the way source is, but it isn't opaque either. It carries its own metadata: `file` reports the architecture and bitness, `checksec` reports which memory protections the compiler switched on, `nm` and `strings` leak function names and literal text, and `objdump` turns the instructions back into assembly.

That metadata is most of the work. Every binary I meet is some combination of:

* **32-bit or 64-bit** — decides pointer size, register names, and calling convention
* **an architecture** — x86, ARM, MIPS
* **a set of protections** — NX, canary, PIE, RELRO
* **a vulnerability** that reduces to one of a handful of known *shapes*

Identify those four quickly and the path is about 80% decided. The remaining work is mechanical: find where input corrupts memory, measure how far it is to the return address, pick the shape the protections allow, build the payload, verify locally, aim at remote.

The module is written in first person on purpose — it is the working map I use to walk a new target, not a cold reference.

**Start here → [binary-exploitation/](binary-exploitation/)** — the map, the exploit shapes, and the offset tooling.

## Usage

Each directory contains documentation regarding the purpose and deployment of the included scripts.

## Standards

This repository follows standard open-source documentation conventions.

### Tooling

The suite is Python and shell. Quality checks (`compileall` over all first-party Python, a regression suite for the binary-exploitation tooling, and `bash -n` over every script) run from `.github/workflows/quality-gate.yml`, and can be run locally with:

```bash
npm run check   # byte-compile all first-party Python
npm test        # run the regression suite
```

---
*Disclaimer: All tools and scripts are intended for authorized penetration testing and educational purposes only.*
