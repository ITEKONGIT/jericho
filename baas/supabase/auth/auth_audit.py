#!/usr/bin/env python3
"""
Jericho Supabase Auth Auditor
Tests authentication configurations and provider security
"""

import requests
import json
import argparse
import sys
import re

class AuthAuditor:
    def __init__(self, url, anon_key):
        self.url = url.rstrip('/')
        self.anon_key = anon_key
        self.headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        }
        self.findings = []
    
    def get_auth_settings(self):
        """Fetch auth configuration"""
        print("[*] Fetching auth settings...")
        try:
            r = requests.get(
                f"{self.url}/auth/v1/settings",
                headers=self.headers
            )
            if r.status_code == 200:
                return r.json()
            else:
                print(f"[-] Auth settings not accessible: {r.status_code}")
                return None
        except Exception as e:
            print(f"[-] Error: {e}")
            return None
    
    def test_email_verification(self):
        """Test if email verification is required"""
        print("[*] Testing email verification requirements...")
        
        # Try to sign up without verification
        test_email = f"test_{__import__('random').randint(1000,9999)}@example.com"
        test_password = "Test123!@#"
        
        try:
            r = requests.post(
                f"{self.url}/auth/v1/signup",
                json={
                    "email": test_email,
                    "password": test_password
                },
                headers=self.headers
            )
            
            if r.status_code == 200:
                data = r.json()
                if data.get('user'):
                    user = data['user']
                    if not user.get('confirmed_at'):
                        print("[!] Email verification NOT required (users can sign up without verification)")
                        self.findings.append({
                            "severity": "HIGH",
                            "finding": "Missing email verification",
                            "detail": "New users can sign up without email confirmation"
                        })
                    else:
                        print("[+] Email verification is enabled")
            else:
                print(f"[-] Signup test failed: {r.status_code}")
        except Exception as e:
            print(f"[-] Signup test error: {e}")
    
    def test_mfa(self):
        """Check MFA configuration"""
        print("[*] Testing MFA configuration...")
        # This is a basic check - MFA is typically enabled via Supabase dashboard
        # We can check if MFA endpoints exist and are accessible
        
        try:
            # Check MFA enrollment endpoint
            r = requests.get(
                f"{self.url}/auth/v1/factors",
                headers=self.headers
            )
            if r.status_code == 401 or r.status_code == 403:
                print("[!] MFA endpoints exist but require authentication")
                print("[*] Consider testing MFA policy during authenticated sessions")
            else:
                print(f"[*] MFA endpoint response: {r.status_code}")
        except Exception as e:
            print(f"[-] MFA check failed: {e}")
    
    def check_redirect_validation(self):
        """Check OAuth redirect URL validation"""
        print("[*] Checking redirect URL validation...")
        
        # Test with an invalid redirect URL
        test_redirects = [
            "https://attacker.com/callback",
            "https://evil-site.com/auth",
            "http://localhost:8080/callback"
        ]
        
        for redirect in test_redirects:
            try:
                # Try to initiate OAuth flow with custom redirect
                params = {
                    "provider": "google",
                    "redirect_to": redirect
                }
                r = requests.get(
                    f"{self.url}/auth/v1/authorize",
                    params=params,
                    headers=self.headers,
                    allow_redirects=False
                )
                
                if r.status_code == 200 or r.status_code == 302:
                    print(f"[!] Potential redirect vulnerability: {redirect}")
                    self.findings.append({
                        "severity": "MEDIUM",
                        "finding": "Weak redirect validation",
                        "detail": f"Redirect to {redirect} is allowed"
                    })
            except Exception as e:
                pass
    
    def enumerate_providers(self):
        """List enabled auth providers"""
        print("[*] Enumerating enabled OAuth providers...")
        
        providers = ["google", "github", "gitlab", "facebook", "twitter", "apple", "azure", "discord", "slack"]
        enabled = []
        
        for provider in providers:
            try:
                r = requests.get(
                    f"{self.url}/auth/v1/authorize",
                    params={"provider": provider},
                    headers=self.headers,
                    allow_redirects=False
                )
                if r.status_code == 302 or r.status_code == 200:
                    enabled.append(provider)
                    print(f"[+] {provider} is enabled")
            except:
                pass
        
        if enabled:
            print(f"[*] Enabled providers: {', '.join(enabled)}")
            self.findings.append({
                "severity": "INFO",
                "finding": "Enabled OAuth providers",
                "detail": f"Providers: {', '.join(enabled)}"
            })
        return enabled
    
    def run(self):
        """Run full auth audit"""
        print("="*60)
        print("JERICHO SUPABASE AUTH AUDITOR")
        print("="*60)
        
        settings = self.get_auth_settings()
        if settings:
            print("[+] Auth settings retrieved")
        
        self.test_email_verification()
        self.test_mfa()
        self.check_redirect_validation()
        enabled_providers = self.enumerate_providers()
        
        print("\n" + "="*60)
        print("AUTH AUDIT SUMMARY")
        print("="*60)
        print(f"Findings: {len(self.findings)}")
        for finding in self.findings:
            print(f"[{finding['severity']}] {finding['finding']}")
        
        # Save findings
        with open('auth_findings.json', 'w') as f:
            json.dump(self.findings, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Auth Auditor")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    args = parser.parse_args()
    
    auditor = AuthAuditor(args.url, args.key)
    auditor.run()

if __name__ == "__main__":
    main()
