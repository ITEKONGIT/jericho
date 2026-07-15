#!/usr/bin/env python3
"""
Jericho Supabase Arsenal - Master Orchestrator
Runs all Supabase audit modules and generates a comprehensive report
"""

import subprocess
import sys
import os
import argparse
import json
from datetime import datetime

class SupabaseArsenal:
    def __init__(self, url, anon_key, authenticated_jwt=None):
        self.url = url
        self.anon_key = anon_key
        self.authenticated_jwt = authenticated_jwt
        self.modules = [
            ('reconnaissance/project_mapper.py', 'Project Mapper'),
            ('auth/auth_audit.py', 'Auth Auditor'),
            ('database/rls_audit.py', 'RLS Auditor'),
            ('database/schema_enum.py', 'Schema Enumerator'),
            ('database/function_audit.py', 'Function Auditor'),
            ('storage/bucket_audit.py', 'Storage Auditor'),
            ('realtime/channel_audit.py', 'Realtime Auditor'),
        ]
        self.secrets_module = ('secrets/key_exposure.py', 'Key Exposure Scanner')
        self.results = {}
    
    def run_module(self, script, name):
        """Run a single module"""
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print('='*60)
        
        cmd = [
            'python3', script,
            '-u', self.url,
            '-k', self.anon_key
        ]
        
        if self.authenticated_jwt and 'rls_audit' in script:
            cmd.extend(['-a', self.authenticated_jwt])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            
            # Check if module produced a JSON output file
            output_file = script.replace('.py', '') + '.json'
            if script.startswith('database/'):
                output_file = script.replace('database/', '').replace('.py', '') + '.json'
            elif script.startswith('reconnaissance/'):
                output_file = 'recon_results.json'
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    self.results[name] = json.load(f)
            else:
                # Try to find any JSON file created
                for file in os.listdir('.'):
                    if file.endswith('.json') and file not in self.results:
                        try:
                            with open(file, 'r') as f:
                                self.results[file.replace('.json', '')] = json.load(f)
                        except:
                            pass
            
            return result.returncode == 0
        except Exception as e:
            print(f"[-] Error running {name}: {e}")
            return False
    
    def run_secrets_scan(self, target_url):
        """Run key exposure scanner on a target"""
        print(f"\n{'='*60}")
        print("Running: Key Exposure Scanner")
        print('='*60)
        
        cmd = [
            'python3', 'secrets/key_exposure.py',
            '-u', target_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            
            if os.path.exists('key_exposure.json'):
                with open('key_exposure.json', 'r') as f:
                    self.results['Key Exposure Scanner'] = json.load(f)
            
            return result.returncode == 0
        except Exception as e:
            print(f"[-] Error running key exposure scanner: {e}")
            return False
    
    def run_all(self):
        """Run all modules"""
        print("="*60)
        print("JERICHO SUPABASE ARSENAL")
        print(f"Target: {self.url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        success = 0
        total = 0
        
        for script, name in self.modules:
            total += 1
            if self.run_module(script, name):
                success += 1
        
        # Run secrets scanner separately (needs target URL)
        print("\n[*] Secrets scanner requires a target URL to scan")
        secrets_target = input("Enter target URL for key exposure scan (or press Enter to skip): ").strip()
        if secrets_target:
            total += 1
            if self.run_secrets_scan(secrets_target):
                success += 1
        
        # Generate report
        print(f"\n{'='*60}")
        print(f"Completed: {success}/{total} modules successful")
        
        if os.path.exists('report/findings.py'):
            print("\n[*] Generating final report...")
            subprocess.run(['python3', 'report/findings.py'])
        else:
            print("[-] Report generator not found")
    
    def run_single(self, module_name):
        """Run a single module by name"""
        module_map = {
            'project_mapper': ('reconnaissance/project_mapper.py', 'Project Mapper'),
            'auth': ('auth/auth_audit.py', 'Auth Auditor'),
            'rls': ('database/rls_audit.py', 'RLS Auditor'),
            'schema': ('database/schema_enum.py', 'Schema Enumerator'),
            'functions': ('database/function_audit.py', 'Function Auditor'),
            'storage': ('storage/bucket_audit.py', 'Storage Auditor'),
            'realtime': ('realtime/channel_audit.py', 'Realtime Auditor'),
            'secrets': ('secrets/key_exposure.py', 'Key Exposure Scanner'),
            'report': ('report/findings.py', 'Report Generator'),
        }
        
        if module_name not in module_map:
            print(f"Available modules: {', '.join(module_map.keys())}")
            return
        
        script, name = module_map[module_name]
        if 'secrets' in script:
            target = input("Enter target URL to scan: ").strip()
            if target:
                self.run_secrets_scan(target)
        elif 'report' in script:
            subprocess.run(['python3', script])
        else:
            self.run_module(script, name)

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Arsenal")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    parser.add_argument("-a", "--auth", help="Authenticated JWT token")
    parser.add_argument("-m", "--module", help="Run specific module only")
    args = parser.parse_args()
    
    arsenal = SupabaseArsenal(args.url, args.key, args.auth)
    
    if args.module:
        arsenal.run_single(args.module)
    else:
        arsenal.run_all()

if __name__ == "__main__":
    main()
