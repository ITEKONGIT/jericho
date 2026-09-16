# Cloud Enumeration and Host Security Auditing

This directory serves as the home for our internal security assessments, host hardening, and cloud-native exploitation research. Much like the wisdom in Proverbs 27:12—"The prudent see danger and take refuge, but the simple keep going and pay the penalty"—this suite is built to help us see the vulnerabilities before they become a liability.

## Linux Host Security

- **Host-Audit/**: Our Linux host hardening toolkit.
  - `linux-host-audit.sh` is the automated bash utility we reach for first: metadata SSRF checks (critical for DigitalOcean and other cloud-native setups), Docker daemon configuration review so we aren't running as unrestricted root, SSH daemon hardening, and system integrity checks via AppArmor and auditd.
  - `README.md` breaks every check out into an individual copy-pasteable command, for when the script can't run on the target or when the audit needs to be done step by step.

## Cloud Provider Exploitation

This section contains our research methodology and the tactical scripts we use in the field.

### AWS (Amazon Web Services)
- **aws/lateral-movement.md**: Our current notes on navigating AWS IAM and privilege escalation paths.
- **aws/scripts/**: Home to tools like console_federator.py, used for handling federated session exploitation.

### GCP (Google Cloud Platform)
- **gcp/gcp-exploitation.md**: Our evolving playbook for enumerating GCP service accounts and finding escalation vectors.
- **gcp/scripts/**: A dedicated space for GCP-specific reconnaissance tools as we develop them.

### Azure
- **azure/azure-exploitation.md**: Tactics for mapping Azure AD (Entra ID) and tenant-level enumeration.
- **azure/scripts/**: Reserved for our Azure-specific offensive tooling.

## How to use this

Most of these tools—especially the host audits—require root privileges to be effective. As we grow the arsenal, please ensure that any new scripts you add to the provider directories are linked back to their corresponding research notes in the Markdown files. We need to keep the "why" just as accessible as the "how."

The procedure these tools implement lives in **`../docs/Infra-Security-Assessment-Checklist.md`** — pre-engagement authorization gates, external attack-surface enumeration, host-level misconfiguration auditing with expected vulnerable/hardened output per check, and cloud config review. Start there, and reach for the scripts in this directory when a step calls for one; the tooling is only useful alongside the reasoning that says when to run it and what a clean result actually means.
