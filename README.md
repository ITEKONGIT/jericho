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
