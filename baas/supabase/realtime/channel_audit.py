#!/usr/bin/env python3
"""
Jericho Supabase Realtime Auditor
Checks realtime channel accessibility and permissions
"""

import requests
import json
import argparse
import sys
import time

class RealtimeAuditor:
    def __init__(self, url, key):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        self.findings = []
    
    def test_realtime(self):
        """Test realtime endpoint accessibility"""
        print("[*] Testing realtime service...")
        
        # Check if realtime service is available
        realtime_endpoint = f"{self.url}/realtime/v1/websocket"
        
        try:
            # Try HTTP upgrade to see if service exists
            r = requests.get(
                realtime_endpoint,
                headers=self.headers,
                timeout=5
            )
            
            if r.status_code != 404:
                print(f"[+] Realtime service available (status: {r.status_code})")
                return True
            else:
                print("[-] Realtime service not found")
                return False
        except requests.exceptions.Timeout:
            print("[i] Realtime service may exist (connection timed out)")
            return True
        except Exception as e:
            print(f"[-] Realtime check failed: {e}")
            return False
    
    def test_public_channel(self):
        """Test access to public channels"""
        print("\n[*] Testing public channel access...")
        
        # Common channel names to test
        channels = [
            'public',
            'realtime', 
            'events',
            'notifications',
            'messages',
            'updates',
            'all',
            'broadcast',
            'public:all',
            'public:*'
        ]
        
        accessible = []
        
        for channel in channels:
            try:
                # Try to get channel info
                r = requests.get(
                    f"{self.url}/realtime/v1/channels/{channel}",
                    headers=self.headers,
                    timeout=3
                )
                
                if r.status_code == 200:
                    accessible.append(channel)
                    print(f"[+] Channel accessible: {channel}")
                    self.findings.append({
                        'severity': 'MEDIUM',
                        'finding': f'Public realtime channel: {channel}',
                        'detail': f'Channel {channel} is accessible without authentication'
                    })
                elif r.status_code == 404:
                    print(f"[-] Channel not found: {channel}")
                elif r.status_code == 403:
                    print(f"[!] Channel requires auth: {channel}")
            except:
                pass
        
        return accessible
    
    def test_authenticated_access(self):
        """Test if authentication is required for realtime"""
        print("\n[*] Testing authentication requirements...")
        
        # Test with no auth headers
        try:
            r = requests.get(
                f"{self.url}/realtime/v1/websocket",
                timeout=3
            )
            
            # If we get a response, auth might not be required
            if r.status_code != 401 and r.status_code != 403:
                print("[!] Realtime accessible without authentication")
                self.findings.append({
                    'severity': 'HIGH',
                    'finding': 'Realtime service lacks authentication',
                    'detail': 'Realtime WebSocket accessible without API key'
                })
            else:
                print("[+] Authentication required for realtime")
        except:
            print("[i] Could not determine auth requirements")
    
    def run(self):
        """Run full realtime audit"""
        print("="*60)
        print("JERICHO SUPABASE REALTIME AUDITOR")
        print("="*60)
        
        if not self.test_realtime():
            print("[-] Realtime service not available")
            return
        
        self.test_public_channel()
        self.test_authenticated_access()
        
        print("\n" + "="*60)
        print("REALTIME AUDIT SUMMARY")
        print("="*60)
        
        if self.findings:
            print(f"[!] Found {len(self.findings)} issues:")
            for finding in self.findings:
                print(f"[{finding['severity']}] {finding['finding']}")
                print(f"    {finding['detail']}\n")
        else:
            print("[+] No realtime security issues found")
        
        # Save results
        with open('realtime_audit.json', 'w') as f:
            json.dump(self.findings, f, indent=2)
        print("[*] Results saved to realtime_audit.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Realtime Auditor")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    args = parser.parse_args()
    
    auditor = RealtimeAuditor(args.url, args.key)
    auditor.run()

if __name__ == "__main__":
    main()
