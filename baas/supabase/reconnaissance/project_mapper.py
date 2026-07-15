#!/usr/bin/env python3
"""
Jericho Supabase Project Mapper
Discovers all exposed database objects via PostgREST introspection
"""

import requests
import json
import argparse
import sys
from urllib.parse import urljoin

class SupabaseMapper:
    def __init__(self, url, anon_key):
        self.url = url.rstrip('/')
        self.anon_key = anon_key
        self.headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        }
        self.findings = {
            "tables": [],
            "views": [],
            "functions": [],
            "exposed_schemas": []
        }
    
    def get_openapi(self):
        """Fetch the OpenAPI specification"""
        print("[*] Fetching OpenAPI specification...")
        try:
            r = requests.get(f"{self.url}/rest/v1/", headers=self.headers)
            if r.status_code == 200:
                spec = r.json()
                self.parse_spec(spec)
                return spec
            else:
                print(f"[-] Failed to fetch spec: {r.status_code}")
                return None
        except Exception as e:
            print(f"[-] Error: {e}")
            return None
    
    def parse_spec(self, spec):
        """Parse OpenAPI spec for exposed objects"""
        if 'paths' not in spec:
            return
            
        for path, methods in spec['paths'].items():
            # Tables and views are under /rest/v1/{table_name}
            if path.startswith('/'):
                parts = path.strip('/').split('/')
                if len(parts) == 1:  # /table_name
                    table_name = parts[0]
                    if not table_name.startswith('_'):
                        self.findings['tables'].append(table_name)
                        print(f"[+] Found table: {table_name}")
                elif len(parts) == 2 and parts[0] == 'rpc':  # /rpc/function_name
                    func_name = parts[1]
                    self.findings['functions'].append(func_name)
                    print(f"[+] Found RPC function: {func_name}")
    
    def probe_table_schema(self, table):
        """Get table structure by requesting one row with limit=0"""
        print(f"[*] Probing schema for: {table}")
        try:
            r = requests.get(
                f"{self.url}/rest/v1/{table}?select=*&limit=0",
                headers=self.headers
            )
            if r.status_code == 200:
                # Check Content-Range header for column info
                if 'content-range' in r.headers:
                    print(f"[+] Table {table} is accessible")
                    return True
                # Try to get column names from first record
                if r.json() and len(r.json()) > 0:
                    columns = list(r.json()[0].keys())
                    print(f"[+] Columns in {table}: {', '.join(columns)}")
                    return True
            else:
                print(f"[-] {table} not accessible: {r.status_code}")
                return False
        except Exception as e:
            print(f"[-] Error probing {table}: {e}")
            return False
    
    def enumerate_storage(self):
        """Try to list storage buckets"""
        print("\n[*] Checking storage buckets...")
        try:
            r = requests.get(
                f"{self.url}/storage/v1/bucket",
                headers=self.headers
            )
            if r.status_code == 200:
                buckets = r.json()
                if buckets:
                    print(f"[+] Found {len(buckets)} bucket(s):")
                    for bucket in buckets:
                        print(f"    - {bucket.get('name')} (ID: {bucket.get('id')})")
                return buckets
            else:
                print(f"[-] No bucket access: {r.status_code}")
                return []
        except Exception as e:
            print(f"[-] Storage check failed: {e}")
            return []
    
    def run(self):
        """Run full reconnaissance"""
        print("="*60)
        print("JERICHO SUPABASE RECONNAISSANCE")
        print("="*60)
        
        # Get OpenAPI spec
        self.get_openapi()
        
        # Probe discovered tables
        print(f"\n[*] Probes {len(self.findings['tables'])} tables...")
        accessible_tables = []
        for table in self.findings['tables']:
            if self.probe_table_schema(table):
                accessible_tables.append(table)
        
        # Check storage
        buckets = self.enumerate_storage()
        
        # Summary
        print("\n" + "="*60)
        print("RECONNAISSANCE SUMMARY")
        print("="*60)
        print(f"Tables discovered: {len(self.findings['tables'])}")
        print(f"Tables accessible: {len(accessible_tables)}")
        print(f"RPC functions: {len(self.findings['functions'])}")
        print(f"Storage buckets: {len(buckets)}")
        
        # Save results
        with open('recon_results.json', 'w') as f:
            json.dump(self.findings, f, indent=2)
        print("[*] Results saved to recon_results.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Project Mapper")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    args = parser.parse_args()
    
    mapper = SupabaseMapper(args.url, args.key)
    mapper.run()

if __name__ == "__main__":
    main()
