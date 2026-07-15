#!/usr/bin/env python3
"""
Jericho Supabase RLS Auditor
Tests Row Level Security policies on all exposed tables
"""

import requests
import json
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class RLSAuditor:
    def __init__(self, url, anon_key, authenticated_jwt=None):
        self.url = url.rstrip('/')
        self.anon_key = anon_key
        self.authenticated_jwt = authenticated_jwt
        self.headers_anon = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        }
        self.headers_auth = None
        if authenticated_jwt:
            self.headers_auth = {
                "apikey": anon_key,
                "Authorization": f"Bearer {authenticated_jwt}"
            }
        self.findings = []
        self.vulnerabilities = []
    
    def test_table_access(self, table, headers, auth_level):
        """Test if a table is accessible"""
        results = {}
        
        # Test SELECT
        try:
            r = requests.get(
                f"{self.url}/rest/v1/{table}?select=*&limit=1",
                headers=headers
            )
            results['select'] = {
                'status': r.status_code,
                'accessible': r.status_code == 200,
                'data': r.json() if r.status_code == 200 else None
            }
        except:
            results['select'] = {'status': 500, 'accessible': False, 'data': None}
        
        # Test INSERT (with minimal data)
        try:
            r = requests.post(
                f"{self.url}/rest/v1/{table}",
                headers=headers,
                json={}  # Empty object - may fail but test for errors
            )
            results['insert'] = {
                'status': r.status_code,
                'accessible': r.status_code == 201 or r.status_code == 409
            }
        except:
            results['insert'] = {'status': 500, 'accessible': False}
        
        return results
    
    def audit_table(self, table):
        """Full audit of a single table"""
        print(f"\n[*] Auditing table: {table}")
        
        # Test with anon key
        print(f"    Testing with ANON key...")
        anon_results = self.test_table_access(table, self.headers_anon, 'anon')
        
        # Test with authenticated JWT if available
        auth_results = None
        if self.headers_auth:
            print(f"    Testing with AUTHENTICATED JWT...")
            auth_results = self.test_table_access(table, self.headers_auth, 'authenticated')
        
        # Analyze findings
        finding = {
            'table': table,
            'anon_read': anon_results['select']['accessible'],
            'anon_insert': anon_results['insert']['accessible'],
            'authenticated_read': auth_results['select']['accessible'] if auth_results else None,
            'authenticated_insert': auth_results['insert']['accessible'] if auth_results else None,
            'raw_anon': anon_results,
            'raw_auth': auth_results
        }
        
        # Severity assessment
        if anon_results['select']['accessible'] and anon_results['select']['data']:
            severity = "CRITICAL"
            detail = f"Table {table} is fully readable by ANON key"
            self.vulnerabilities.append({
                'severity': severity,
                'finding': f"RLS missing on {table}",
                'detail': detail,
                'evidence': anon_results['select']['data'][:1]  # First row as evidence
            })
            print(f"    [!] {severity}: {detail}")
        
        elif anon_results['select']['accessible']:
            print(f"    [!] Table accessible but empty (may still be vulnerable)")
        
        if anon_results['insert']['accessible']:
            severity = "HIGH"
            detail = f"Table {table} allows inserts with ANON key"
            self.vulnerabilities.append({
                'severity': severity,
                'finding': f"Unrestricted inserts on {table}",
                'detail': detail
            })
            print(f"    [!] {severity}: {detail}")
        
        # Check for authenticated-only access (but missing ownership checks)
        if auth_results and auth_results['select']['accessible']:
            if anon_results['select']['accessible'] is False:
                print(f"    [i] Table protected from ANON, accessible with AUTH")
                # This is good, but we need to test ownership
                
        return finding
    
    def enumerate_tables(self):
        """Get list of tables from OpenAPI"""
        print("[*] Discovering tables via OpenAPI...")
        try:
            r = requests.get(f"{self.url}/rest/v1/", headers=self.headers_anon)
            if r.status_code == 200:
                spec = r.json()
                tables = []
                if 'paths' in spec:
                    for path in spec['paths'].keys():
                        if path.startswith('/') and not path.startswith('/rpc'):
                            table = path.strip('/')
                            if table and not table.startswith('_'):
                                tables.append(table)
                print(f"[+] Found {len(tables)} tables")
                return tables
            else:
                print(f"[-] Failed to get OpenAPI spec: {r.status_code}")
                return []
        except Exception as e:
            print(f"[-] Error: {e}")
            return []
    
    def run(self):
        """Run full RLS audit"""
        print("="*60)
        print("JERICHO SUPABASE RLS AUDITOR")
        print("="*60)
        
        tables = self.enumerate_tables()
        if not tables:
            print("[-] No tables discovered. Check URL and key.")
            return
        
        print(f"[*] Auditing {len(tables)} tables...\n")
        
        results = {}
        for table in tables:
            try:
                results[table] = self.audit_table(table)
            except Exception as e:
                print(f"[-] Error auditing {table}: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("RLS AUDIT SUMMARY")
        print("="*60)
        
        if self.vulnerabilities:
            print(f"\n[!] Found {len(self.vulnerabilities)} vulnerabilities:")
            for vuln in self.vulnerabilities:
                print(f"[{vuln['severity']}] {vuln['finding']}")
                print(f"    {vuln['detail']}\n")
        else:
            print("[+] No critical RLS issues detected")
        
        # Save results
        with open('rls_audit_results.json', 'w') as f:
            json.dump({
                'results': results,
                'vulnerabilities': self.vulnerabilities
            }, f, indent=2)
        print("[*] Results saved to rls_audit_results.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase RLS Auditor")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    parser.add_argument("-a", "--auth", help="Authenticated JWT token (for testing authenticated policies)")
    args = parser.parse_args()
    
    auditor = RLSAuditor(args.url, args.key, args.auth)
    auditor.run()

if __name__ == "__main__":
    main()
