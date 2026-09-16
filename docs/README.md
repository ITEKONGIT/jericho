# DOCUMENTATION & CHECKLISTS

Standardized assessment methodologies and operational security checklists — the "why" behind the techniques, kept next to the tooling that implements them.

## Newcomer ramp

**What this directory is.** The reasoning layer for the rest of Jericho. Module READMEs say *how to run it*; these documents say *why it works, why it fails, and what to conclude from each outcome*. Read a methodology doc before its matching module and the tool output becomes interpretable; skip it and the tool is a slot machine.

**Why this layer gets missed.** Tool output arrives as an answer, and answers get copy-pasted into reports. The methodology docs exist because the same output means different things in different contexts — a clean host-audit result from a least-privileged account is not a clean host. The recurring miss: **running the tool without owning the reasoning that says when to run it and what a clean result actually means.**

**Read order.** If the target has a frontend, [`methodology/frontend-encryption.md`](methodology/frontend-encryption.md) — it teaches the trace-from-the-bundle habit that generalizes far beyond crypto. If there's a mobile target, [`methodology/mobile-reversing.md`](methodology/mobile-reversing.md). [`Infra-Security-Assessment-Checklist.md`](Infra-Security-Assessment-Checklist.md) is the entry point for infrastructure work and the parent of the cloud-enum tooling. And [`classes-people-miss.md`](classes-people-miss.md) is the shelf of bug classes that don't appear as named types anywhere — start there when the question is "what am I probably overlooking?"

## Methodology

- **methodology/frontend-encryption.md** — Frontend Encryption Analysis. Where client-side crypto actually breaks down: key derivation (KDFs, salts, iteration counts), the developer's own encryption lifecycle, and a trace workflow that starts from the JavaScript bundle rather than from the cipher name.
- **methodology/mobile-reversing.md** — Hardened SSL Pinning & Obfuscation Analysis. What to do when automated interception fails: telemetry capture and protocol analysis, port normalization for backends that dodge 443/80, and native-layer pinning that Java-level Frida hooks will not touch.

## Checklists

- **Infra-Security-Assessment-Checklist.md** — Infrastructure Security Assessment Checklist (DigitalOcean / Hetzner focus). Pre-engagement and authorization gates, external cloud attack-surface enumeration, host-level misconfiguration auditing with expected vulnerable/hardened output per check, cloud config review, and the caveats for running the host checks as a least-privileged account.
