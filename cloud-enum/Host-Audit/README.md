# Linux Host Security Audit - Individual Commands

This document contains all security audit checks broken down into individual commands that can be copy-pasted directly into a shell.

## Prerequisites
- Root/sudo access recommended for full visibility
- Bash shell

---

## 1. CHECK PENDING SECURITY UPDATES

### Debian/Ubuntu:
```bash
apt list --upgradable 2>/dev/null | grep -c security || echo "0"
RHEL/CentOS:
bash
yum check-update --security 2>/dev/null | grep -c "^[a-zA-Z]" || echo "0"
Fedora:
bash
dnf check-update --security 2>/dev/null | grep -c "^[a-zA-Z]" || echo "0"
2. CHECK REBOOT REQUIRED
bash
[ -f /var/run/reboot-required ] && echo "REBOOT REQUIRED" || echo "No reboot required"
3. CHECK APPARMOR STATUS
bash
if command -v aa-status &> /dev/null; then aa-status 2>/dev/null | grep -q "apparmor module is loaded" && echo "AppArmor is active" || echo "AppArmor is installed but not active"; else echo "AppArmor is not installed"; fi
4. CHECK DOCKER STATUS
bash
if command -v docker &> /dev/null; then echo "Docker is installed"; docker info 2>/dev/null | grep -q "Root Dir: /var/lib/docker" && echo "Docker is running as root (default configuration)"; else echo "Docker is not installed"; fi
5. CHECK DIGITALOCEAN METADATA ACCESS
bash
curl -s --connect-timeout 2 http://169.254.169.254/metadata/v1/ 2>/dev/null | grep -q "interfaces" && echo "DigitalOcean metadata service is accessible (SSRF risk!)" || echo "DigitalOcean metadata service is not accessible"
6. CHECK FAIL2BAN
bash
systemctl is-active --quiet fail2ban 2>/dev/null || pgrep -x "fail2ban" > /dev/null && echo "fail2ban is running" || echo "fail2ban is not installed or not running"
7. SSH SERVER CONFIGURATION CHECKS
Check PermitRootLogin:
bash
[ -f /etc/ssh/sshd_config ] && (grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config || grep -q "^PermitRootLogin without-password" /etc/ssh/sshd_config) && echo "PermitRootLogin is enabled (should be 'no' or 'prohibit-password')" || echo "PermitRootLogin is properly configured"
Check X11Forwarding:
bash
[ -f /etc/ssh/sshd_config ] && grep -q "^X11Forwarding yes" /etc/ssh/sshd_config && echo "X11Forwarding is enabled (security risk)" || echo "X11Forwarding is disabled"
Check MaxAuthTries:
bash
[ -f /etc/ssh/sshd_config ] && MAXAUTH=$(grep "^MaxAuthTries" /etc/ssh/sshd_config | awk '{print $2}') && [ -n "$MAXAUTH" ] && ([ "$MAXAUTH" -gt 3 ] && echo "MaxAuthTries is set to $MAXAUTH (recommended: 3 or less)" || echo "MaxAuthTries is set to $MAXAUTH (good)") || echo "MaxAuthTries not set (default is 6 - consider reducing)"
8. CHECK SUDO CONFIGURATION
bash
[ -f /etc/sudoers ] && grep -q "NOPASSWD: ALL" /etc/sudoers && echo "NOPASSWD: ALL found in sudoers (passwordless sudo for everything!)" || echo "No passwordless ALL sudo entries found"
9. CHECK ROOT LOGINS / USER PRIVILEGES
bash
USER_COUNT=$(awk -F: '$3 >= 1000 && $1 != "nobody" {print $1}' /etc/passwd | wc -l); [ "$USER_COUNT" -eq 0 ] && echo "Only root user detected - all logins are root level" || echo "$USER_COUNT non-root users exist on the system"
10. CHECK MOUNT OPTIONS
bash
mount | grep "^/dev" | while IFS= read -r line; do MOUNT_POINT=$(echo "$line" | awk '{print $2}'); if [ "$MOUNT_POINT" != "/" ] && [ "$MOUNT_POINT" != "/boot" ] && [ "$MOUNT_POINT" != "/boot/efi" ]; then ! echo "$line" | grep -q "noexec" && echo "$MOUNT_POINT lacks noexec"; ! echo "$line" | grep -q "nosuid" && echo "$MOUNT_POINT lacks nosuid"; ! echo "$line" | grep -q "nodev" && echo "$MOUNT_POINT lacks nodev"; fi; done
11. CHECK AUDITD
bash
systemctl is-active --quiet auditd 2>/dev/null || pgrep -x "auditd" > /dev/null && echo "auditd is running" || echo "auditd is not running (audit framework inactive)"
12. CHECK WORLD-WRITABLE FILES
bash
if command -v find &> /dev/null; then WW_FILES=$(find / -type f -perm -002 2>/dev/null | wc -l); [ "$WW_FILES" -gt 0 ] && echo "Found $WW_FILES world-writable files" || echo "No world-writable files found"; fi
Show sample of world-writable files:
bash
if command -v find &> /dev/null; then WW_FILES=$(find / -type f -perm -002 2>/dev/null | wc -l); [ "$WW_FILES" -gt 0 ] && [ "$WW_FILES" -gt 10 ] && echo "Sample of world-writable files:" && find / -type f -perm -002 2>/dev/null | head -5; fi
13. COMPLETE SYSTEM AUDIT (Run All Checks)
One-liner to run everything:
bash
echo "=== SYSTEM SECURITY AUDIT ==="; echo "1. Security Updates:"; apt list --upgradable 2>/dev/null | grep -c security || echo "0"; echo "2. Reboot Required:"; [ -f /var/run/reboot-required ] && echo "YES" || echo "NO"; echo "3. AppArmor:"; command -v aa-status &> /dev/null && (aa-status 2>/dev/null | grep -q "apparmor module is loaded" && echo "Active" || echo "Installed but inactive") || echo "Not installed"; echo "4. Docker:"; command -v docker &> /dev/null && echo "Installed" || echo "Not installed"; echo "5. DigitalOcean Metadata:"; curl -s --connect-timeout 2 http://169.254.169.254/metadata/v1/ 2>/dev/null | grep -q "interfaces" && echo "ACCESSIBLE" || echo "Not accessible"; echo "6. fail2ban:"; systemctl is-active --quiet fail2ban 2>/dev/null || pgrep -x "fail2ban" > /dev/null && echo "Running" || echo "Not running"; echo "7. SSH RootLogin:"; [ -f /etc/ssh/sshd_config ] && (grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config || grep -q "^PermitRootLogin without-password" /etc/ssh/sshd_config) && echo "ENABLED" || echo "Properly configured"; echo "8. Sudo NOPASSWD:"; [ -f /etc/sudoers ] && grep -q "NOPASSWD: ALL" /etc/sudoers && echo "FOUND" || echo "Not found"; echo "9. Non-root users:"; awk -F: '$3 >= 1000 && $1 != "nobody" {print $1}' /etc/passwd | wc -l; echo "10. auditd:"; systemctl is-active --quiet auditd 2>/dev/null || pgrep -x "auditd" > /dev/null && echo "Running" || echo "Not running"
Quick Reference: Remediation Commands
Apply security updates:
bash
# Debian/Ubuntu
sudo apt update && sudo apt upgrade -y

# RHEL/CentOS
sudo yum update -y

# Fedora
sudo dnf update -y
Install fail2ban:
bash
# Debian/Ubuntu
sudo apt install fail2ban -y

# RHEL/CentOS/Fedora
sudo yum install fail2ban -y
Harden SSH (disable root login):
bash
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
Disable X11Forwarding in SSH:
bash
sudo sed -i 's/^X11Forwarding yes/X11Forwarding no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
Remove passwordless sudo:
bash
sudo visudo
# Comment out or remove lines with NOPASSWD: ALL
Start auditd:
bash
sudo systemctl enable auditd && sudo systemctl start auditd
Generated from linux-host-audit.sh
