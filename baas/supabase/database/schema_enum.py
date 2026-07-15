#!/usr/bin/env python3
"""
Jericho Supabase Schema Enumerator
Enumerates database schema including columns, types, and relationships
"""

import requests
import json
import argparse
import sys

class SchemaEnumerator:
    def __init__(self, url, key, is_service_role=False):
        self.url = url.rstrip('/')
        self.key = key
        self.is_service_role = is_service_role
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        self.schema = {
            'tables': {},
            'views': {},
            'functions': [],
            'enums': {}
        }
    
    def query_metadata(self):
        """Query PostgreSQL metadata via SQL endpoint"""
        print("[*] Attempting to query metadata...")
        
        # Try to query information_schema
        queries = [
            # This requires direct SQL access
            """
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """,
            
            # Alternative: try to get via RPC if available
            """
            SELECT schemaname, tablename, tableowner
            FROM pg_tables
            WHERE schemaname = 'public'
            """
        ]
        
        # Supabase has a /rest/v1/rpc endpoint for executing functions
        # We need to find a function that gives us schema info
        
        # Check if there's a function to get tables
        rpc_functions = ['get_tables', 'list_tables', 'get_schema', 'table_info']
        
        for func in rpc_functions:
            try:
                r = requests.post(
                    f"{self.url}/rest/v1/rpc/{func}",
                    headers=self.headers,
                    json={}
                )
                if r.status_code == 200:
                    print(f"[+] Found RPC function: {func}")
                    return r.json()
            except:
                pass
        
        # Fallback: Parse from OpenAPI
        return self.parse_openapi()
    
    def parse_openapi(self):
        """Parse schema from OpenAPI specification"""
        print("[*] Parsing schema from OpenAPI...")
        
        try:
            r = requests.get(f"{self.url}/rest/v1/", headers=self.headers)
            if r.status_code != 200:
                print(f"[-] Failed to fetch OpenAPI: {r.status_code}")
                return
            
            spec = r.json()
            
            # Look for schemas in components
            if 'components' in spec and 'schemas' in spec['components']:
                schemas = spec['components']['schemas']
                for name, schema in schemas.items():
                    if name.endswith('_table'):
                        table_name = name.replace('_table', '')
                        if 'properties' in schema:
                            columns = {}
                            for prop, details in schema['properties'].items():
                                columns[prop] = details.get('type', 'unknown')
                            self.schema['tables'][table_name] = {
                                'columns': columns,
                                'schema': schema
                            }
                            print(f"[+] Found table: {table_name} ({len(columns)} columns)")
            
            # Look for paths that indicate tables
            if 'paths' in spec:
                for path in spec['paths'].keys():
                    if path.startswith('/') and not path.startswith('/rpc'):
                        table = path.strip('/')
                        if table and not table.startswith('_'):
                            if table not in self.schema['tables']:
                                self.schema['tables'][table] = {'columns': {}, 'schema': {}}
                                print(f"[+] Found additional table: {table}")
            
            return spec
            
        except Exception as e:
            print(f"[-] Error parsing OpenAPI: {e}")
            return None
    
    def probe_columns(self, table):
        """Probe columns by requesting data with limit=1"""
        print(f"[*] Probing columns for: {table}")
        
        try:
            r = requests.get(
                f"{self.url}/rest/v1/{table}?select=*&limit=1",
                headers=self.headers
            )
            
            if r.status_code == 200:
                data = r.json()
                if data and len(data) > 0:
                    columns = list(data[0].keys())
                    col_types = {}
                    for key, value in data[0].items():
                        col_types[key] = type(value).__name__
                    
                    if table in self.schema['tables']:
                        self.schema['tables'][table]['columns'] = col_types
                        self.schema['tables'][table]['sample_data'] = data[0]
                    
                    print(f"[+] Table {table}: {len(columns)} columns - {', '.join(columns)}")
                    return columns
            else:
                print(f"[-] Cannot probe {table}: {r.status_code}")
                return []
        except Exception as e:
            print(f"[-] Error probing {table}: {e}")
            return []
    
    def detect_sensitive_columns(self):
        """Check for common sensitive column names"""
        print("\n[*] Scanning for sensitive columns...")
        
        sensitive_patterns = [
            'password', 'token', 'secret', 'key', 'api_key',
            'email', 'phone', 'address', 'ssn', 'credit_card',
            'passwd', 'pwd', 'auth_token', 'refresh_token',
            'jwt', 'oauth', 'private', 'role', 'admin'
        ]
        
        sensitive = {}
        for table, info in self.schema['tables'].items():
            columns = info.get('columns', {})
            found = [col for col in columns.keys() if any(p in col.lower() for p in sensitive_patterns)]
            if found:
                sensitive[table] = found
                print(f"[!] Sensitive columns in {table}: {', '.join(found)}")
        
        return sensitive
    
    def run(self):
        """Run full schema enumeration"""
        print("="*60)
        print("JERICHO SUPABASE SCHEMA ENUMERATOR")
        print("="*60)
        
        # Try to get metadata
        self.parse_openapi()
        
        # Probe each table for columns
        print(f"\n[*] Probing {len(self.schema['tables'])} tables for column info...")
        for table in self.schema['tables'].keys():
            self.probe_columns(table)
        
        # Detect sensitive columns
        sensitive = self.detect_sensitive_columns()
        
        # Summary
        print("\n" + "="*60)
        print("SCHEMA ENUMERATION SUMMARY")
        print("="*60)
        print(f"Tables discovered: {len(self.schema['tables'])}")
        
        total_columns = sum(len(info.get('columns', {})) for info in self.schema['tables'].values())
        print(f"Total columns: {total_columns}")
        
        if sensitive:
            print(f"[!] Tables with sensitive data: {len(sensitive)}")
        
        # Save results
        with open('schema_enumeration.json', 'w') as f:
            json.dump(self.schema, f, indent=2)
        print("[*] Results saved to schema_enumeration.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Schema Enumerator")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    parser.add_argument("--service-role", action='store_true', help="Use service_role key (bypasses RLS)")
    args = parser.parse_args()
    
    enumerator = SchemaEnumerator(args.url, args.key, args.service_role)
    enumerator.run()

if __name__ == "__main__":
    main()
