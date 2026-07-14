#!/bin/bash

# Security Audit Script for Linux Systems
# Checks for common security misconfigurations and vulnerabilities

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BLUE='\033[0;34m'

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

# Function to print results
print_result() {
    if [ $2 -eq 1 ]; then
        echo -e "${RED}[!] VULNERABLE: $1${NC}"
    else
        echo -e "${GREEN}[✓] OK: $1${NC}"
    fi
}

# Initialize counters
VULNERABLE_COUNT=0
TOTAL_CHECKS=0

echo -e "${BLUE}
╔═══════════════════════════════════════════════════════════╗
║          SYSTEM SECURITY AUDIT SCRIPT                    ║
║          Running comprehensive security checks...        ║
╚═══════════════════════════════════════════════════════════╝${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}[!] Not running as root - some checks may be incomplete${NC}"
fi

# 1. CHECK PENDING SECURITY UPDATES
print_section "Checking Pending Security Updates"
UPDATES=0
if command -v apt &> /dev/null; then
    # Debian/Ubuntu
    UPDATES=$(apt list --upgradable 2>/dev/null | grep -c security || echo "0")
elif command -v yum &> /dev/null; then
    # RHEL/CentOS
    UPDATES=$(yum check-update --security 2>/dev/null | grep -c "^[a-zA-Z]" || echo "0")
elif command -v dnf &> /dev/null; then
    UPDATES=$(dnf check-update --security 2>/dev/null | grep -c "^[a-zA-Z]" || echo "0")
fi

if [ "$UPDATES" -gt 0 ]; then
    echo -e "${RED}[!] Found $UPDATES pending security updates${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
else
    echo -e "${GREEN}[✓] No pending security updates found${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Check if reboot required
if [ -f /var/run/reboot-required ]; then
    echo -e "${RED}[!] System reboot required for updates to take effect${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 2. CHECK APPARMOR STATUS
print_section "Checking AppArmor Status"
if command -v aa-status &> /dev/null; then
    if aa-status 2>/dev/null | grep -q "apparmor module is loaded"; then
        echo -e "${GREEN}[✓] AppArmor is active${NC}"
    else
        echo -e "${RED}[!] AppArmor is installed but not active${NC}"
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    fi
else
    echo -e "${RED}[!] AppArmor is not installed${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 3. CHECK DOCKER STATUS
print_section "Checking Docker Configuration"
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}[!] Docker is installed${NC}"
    if docker info 2>/dev/null | grep -q "Root Dir: /var/lib/docker"; then
        echo -e "${RED}[!] Docker is running as root (default configuration)${NC}"
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    fi
else
    echo -e "${GREEN}[✓] Docker is not installed${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 4. CHECK DIGITALOCEAN METADATA ACCESS
print_section "Checking DigitalOcean Metadata Access"
if curl -s --connect-timeout 2 http://169.254.169.254/metadata/v1/ 2>/dev/null | grep -q "interfaces"; then
    echo -e "${RED}[!] DigitalOcean metadata service is accessible from this VM${NC}"
    echo -e "${RED}    This poses an SSRF (Server-Side Request Forgery) risk!${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
else
    echo -e "${GREEN}[✓] DigitalOcean metadata service is not accessible${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 5. CHECK FAIL2BAN
print_section "Checking Intrusion Prevention"
if systemctl is-active --quiet fail2ban 2>/dev/null || pgrep -x "fail2ban" > /dev/null; then
    echo -e "${GREEN}[✓] fail2ban is running${NC}"
else
    echo -e "${RED}[!] fail2ban is not installed or not running${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 6. CHECK SSH SERVER CONFIGURATION
print_section "Checking SSH Server Configuration"
if [ -f /etc/ssh/sshd_config ]; then
    # Check PermitRootLogin
    if grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config || grep -q "^PermitRootLogin without-password" /etc/ssh/sshd_config; then
        echo -e "${RED}[!] PermitRootLogin is enabled (should be set to 'no' or 'prohibit-password')${NC}"
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    else
        echo -e "${GREEN}[✓] PermitRootLogin is properly configured${NC}"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    # Check X11Forwarding
    if grep -q "^X11Forwarding yes" /etc/ssh/sshd_config; then
        echo -e "${RED}[!] X11Forwarding is enabled (security risk)${NC}"
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    else
        echo -e "${GREEN}[✓] X11Forwarding is disabled${NC}"
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    # Check MaxAuthTries
    MAXAUTH=$(grep "^MaxAuthTries" /etc/ssh/sshd_config | awk '{print $2}')
    if [ -n "$MAXAUTH" ]; then
        if [ "$MAXAUTH" -gt 3 ]; then
            echo -e "${RED}[!] MaxAuthTries is set to $MAXAUTH (recommended: 3 or less)${NC}"
            VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
        else
            echo -e "${GREEN}[✓] MaxAuthTries is set to $MAXAUTH (good)${NC}"
        fi
    else
        echo -e "${RED}[!] MaxAuthTries not set (default is 6 - consider reducing)${NC}"
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
else
    echo -e "${RED}[!] SSH server is not installed or sshd_config not found${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 7. CHECK SUDO CONFIGURATION
print_section "Checking Sudo Configuration"
if [ -f /etc/sudoers ]; then
    if grep -q "NOPASSWD: ALL" /etc/sudoers; then
        echo -e "${RED}[!] NOPASSWD: ALL found in sudoers (allows passwordless sudo for everything)${NC}"
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    else
        echo -e "${GREEN}[✓] No passwordless ALL sudo entries found${NC}"
    fi
else
    echo -e "${YELLOW}[!] sudoers file not found${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 8. CHECK ROOT LOGINS
print_section "Checking User Privileges"
# Check if any non-root users exist
USER_COUNT=$(awk -F: '$3 >= 1000 && $1 != "nobody" {print $1}' /etc/passwd | wc -l)
if [ "$USER_COUNT" -eq 0 ]; then
    echo -e "${RED}[!] Only root user detected - all logins are root level${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
else
    echo -e "${GREEN}[✓] $USER_COUNT non-root users exist on the system${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 9. CHECK MOUNT OPTIONS
print_section "Checking Mount Options"
MOUNT_ISSUES=0
while IFS= read -r line; do
    MOUNT_POINT=$(echo "$line" | awk '{print $2}')
    if [ "$MOUNT_POINT" != "/" ] && [ "$MOUNT_POINT" != "/boot" ] && [ "$MOUNT_POINT" != "/boot/efi" ]; then
        if ! echo "$line" | grep -q "noexec"; then
            echo -e "${RED}[!] $MOUNT_POINT lacks noexec mount option${NC}"
            MOUNT_ISSUES=$((MOUNT_ISSUES + 1))
        fi
        if ! echo "$line" | grep -q "nosuid"; then
            echo -e "${RED}[!] $MOUNT_POINT lacks nosuid mount option${NC}"
            MOUNT_ISSUES=$((MOUNT_ISSUES + 1))
        fi
        if ! echo "$line" | grep -q "nodev"; then
            echo -e "${RED}[!] $MOUNT_POINT lacks nodev mount option${NC}"
            MOUNT_ISSUES=$((MOUNT_ISSUES + 1))
        fi
    fi
done < <(mount | grep "^/dev")

if [ $MOUNT_ISSUES -eq 0 ]; then
    echo -e "${GREEN}[✓] All mount points have proper nosuid,nodev,noexec options${NC}"
else
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + MOUNT_ISSUES))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 10. CHECK AUDITD
print_section "Checking Audit & Logging"
if systemctl is-active --quiet auditd 2>/dev/null || pgrep -x "auditd" > /dev/null; then
    echo -e "${GREEN}[✓] auditd is running${NC}"
else
    echo -e "${RED}[!] auditd is not running (audit framework inactive)${NC}"
    VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# 11. CHECK WORLD-WRITABLE FILES
print_section "Checking World-Writable Files"
if command -v find &> /dev/null; then
    WW_FILES=$(find / -type f -perm -002 2>/dev/null | wc -l)
    if [ "$WW_FILES" -gt 0 ]; then
        echo -e "${RED}[!] Found $WW_FILES world-writable files${NC}"
        # Show a sample of the files
        if [ "$WW_FILES" -gt 10 ]; then
            echo -e "${YELLOW}    Sample of world-writable files:${NC}"
            find / -type f -perm -002 2>/dev/null | head -5 | sed 's/^/    /'
        fi
        VULNERABLE_COUNT=$((VULNERABLE_COUNT + 1))
    else
        echo -e "${GREEN}[✓] No world-writable files found${NC}"
    fi
else
    echo -e "${YELLOW}[!] 'find' command not available${NC}"
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# SUMMARY
print_section "SECURITY AUDIT SUMMARY"
echo -e "Total checks performed: $TOTAL_CHECKS"
echo -e "Vulnerabilities found: $VULNERABLE_COUNT"

if [ $VULNERABLE_COUNT -gt 0 ]; then
    echo -e "\n${RED}⚠️  SECURITY ISSUES DETECTED - RECOMMENDED ACTIONS:${NC}"
    echo -e "${YELLOW}1. Apply all pending security updates and reboot${NC}"
    echo -e "${YELLOW}2. Install and configure fail2ban${NC}"
    echo -e "${YELLOW}3. Harden SSH configuration (disable root login, X11 forwarding)${NC}"
    echo -e "${YELLOW}4. Remove passwordless sudo access${NC}"
    echo -e "${YELLOW}5. Create and use non-root user accounts${NC}"
    echo -e "${YELLOW}6. Configure mount options (nosuid,nodev,noexec)${NC}"
    echo -e "${YELLOW}7. Enable and configure auditd${NC}"
    echo -e "${YELLOW}8. Review and clean up world-writable files${NC}"
    echo -e "${YELLOW}9. Consider using non-root user for Docker${NC}"
    echo -e "${YELLOW}10. Implement network security controls for metadata endpoints${NC}"
else
    echo -e "\n${GREEN}✅ System appears to be well secured!${NC}"
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Audit completed at: $(date)${NC}"
