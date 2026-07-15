#!/usr/bin/env python3
"""
Jericho Supabase Function Auditor
Audits RPC functions for privilege escalation and injection
"""

import requests
import json
import argparse
import sys

class FunctionAuditor:
    def __init__(self, url, key):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        self.functions = []
        self.findings = []
    
    def discover_functions(self):
        """Discover RPC functions from OpenAPI"""
        print("[*] Discovering RPC functions...")
        
        try:
            r = requests.get(f"{self.url}/rest/v1/", headers=self.headers)
            if r.status_code == 200:
                spec = r.json()
                if 'paths' in spec:
                    for path in spec['paths'].keys():
                        if path.startswith('/rpc/'):
                            func = path.replace('/rpc/', '')
                            if func:
                                self.functions.append(func)
                                print(f"[+] Found RPC: {func}")
                return self.functions
            else:
                print(f"[-] Failed to fetch spec: {r.status_code}")
                return []
        except Exception as e:
            print(f"[-] Error: {e}")
            return []
    
    def test_function(self, func):
        """Test a function for accessible execution"""
        print(f"\n[*] Testing function: {func}")
        
        # Try with empty parameters
        try:
            r = requests.post(
                f"{self.url}/rest/v1/rpc/{func}",
                headers=self.headers,
                json={}
            )
            
            if r.status_code == 200:
                print(f"[+] Function {func} is accessible with empty params")
                self.findings.append({
                    'function': func,
                    'accessible': True,
                    'status': '200 OK',
                    'response': r.json() if r.json() else 'Empty response'
                })
                
                # Check if function returns sensitive data
                if r.json():
                    data = r.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"[!] Function returns data: {data[:2]}")  # First 2 items
                        self.findings.append({
                            'function': func,
                            'data_exposed': True,
                            'sample': data[:2]
                        })
                
                return r.json()
            
            elif r.status_code == 400:
                print(f"[i] Function requires parameters (400 Bad Request)")
                # Try common parameters
                common_params = [
                    {}, {'id': 1}, {'limit': 10}, 
                    {'user_id': 'test'}, {'email': 'test@example.com'}
                ]
                for params in common_params:
                    try:
                        r2 = requests.post(
                            f"{self.url}/rest/v1/rpc/{func}",
                            headers=self.headers,
                            json=params
                        )
                        if r2.status_code == 200:
                            print(f"[+] Function accepted params: {params}")
                            return r2.json()
                    except:
                        pass
            else:
                print(f"[-] Function {func} not accessible: {r.status_code}")
                
        except Exception as e:
            print(f"[-] Error testing {func}: {e}")
        
        return None
    
    def detect_sensitive_functions(self):
        """Look for potentially sensitive function names"""
        print("\n[*] Scanning for sensitive functions...")
        
        sensitive_patterns = [
            'admin', 'config', 'system', 'exec', 'command',
            'password', 'reset', 'privilege', 'grant',
            'delete', 'drop', 'truncate', 'backup',
            'export', 'import', 'migrate', 'schema'
        ]
        
        sensitive = []
        for func in self.functions:
            if any(p in func.lower() for p in sensitive_patterns):
                sensitive.append(func)
                print(f"[!] Potentially sensitive function: {func}")
        
        return sensitive
    
    def run(self):
        """Run full function audit"""
        print("="*60)
        print("JERICHO SUPABASE FUNCTION AUDITOR")
        print("="*60)
        
        self.discover_functions()
        
        if not self.functions:
            print("[-] No RPC functions discovered")
            return
        
        print(f"\n[*] Testing {len(self.functions)} functions...")
        for func in self.functions:
            self.test_function(func)
        
        sensitive = self.detect_sensitive_functions()
        
        print("\n" + "="*60)
        print("FUNCTION AUDIT SUMMARY")
        print("="*60)
        print(f"Functions discovered: {len(self.functions)}")
        print(f"Functions accessible: {len([f for f in self.findings if f.get('accessible')])}")
        print(f"Sensitive functions: {len(sensitive)}")
        
        # Save results
        with open('function_audit.json', 'w') as f:
            json.dump({
                'functions': self.functions,
                'findings': self.findings,
                'sensitive': sensitive
            }, f, indent=2)
        print("[*] Results saved to function_audit.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Function Auditor")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    args = parser.parse_args()
    
    auditor = FunctionAuditor(args.url, args.key)
    auditor.run()

if __name__ == "__main__":
    main()
