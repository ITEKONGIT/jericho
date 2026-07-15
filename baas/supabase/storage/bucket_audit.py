#!/usr/bin/env python3
"""
Jericho Supabase Storage Auditor
Audits storage buckets for misconfigurations and exposures
"""

import requests
import json
import argparse
import sys

class StorageAuditor:
    def __init__(self, url, key):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        self.buckets = []
        self.findings = []
    
    def list_buckets(self):
        """List all accessible buckets"""
        print("[*] Listing buckets...")
        
        try:
            r = requests.get(
                f"{self.url}/storage/v1/bucket",
                headers=self.headers
            )
            
            if r.status_code == 200:
                self.buckets = r.json()
                print(f"[+] Found {len(self.buckets)} bucket(s)")
                for bucket in self.buckets:
                    print(f"    - {bucket.get('name')} (public: {bucket.get('public', False)})")
                return self.buckets
            else:
                print(f"[-] Cannot list buckets: {r.status_code}")
                return []
        except Exception as e:
            print(f"[-] Error: {e}")
            return []
    
    def test_bucket_access(self, bucket_name):
        """Test access to a bucket"""
        print(f"\n[*] Testing bucket: {bucket_name}")
        
        # Test listing objects
        results = {}
        
        # Test with anonymous access
        try:
            r_anon = requests.get(
                f"{self.url}/storage/v1/object/list/{bucket_name}",
                headers=self.headers
            )
            results['anonymous'] = {
                'status': r_anon.status_code,
                'accessible': r_anon.status_code == 200
            }
            if r_anon.status_code == 200:
                objects = r_anon.json()
                print(f"[+] ANON access: Can list {len(objects)} objects")
                if objects:
                    # Show first few objects
                    sample = [obj.get('name') for obj in objects[:3]]
                    print(f"[!] Sample objects: {', '.join(sample)}")
                    results['anonymous']['objects'] = objects
                    self.findings.append({
                        'severity': 'HIGH',
                        'finding': f'Public bucket: {bucket_name}',
                        'detail': f'Objects can be listed anonymously',
                        'sample': sample
                    })
            else:
                print(f"[-] ANON access denied: {r_anon.status_code}")
        except Exception as e:
            print(f"[-] Error with anonymous access: {e}")
            results['anonymous'] = {'status': 500, 'accessible': False}
        
        # Test uploading a file
        test_content = "Security test file"
        test_file = f"test_security_{__import__('random').randint(1000,9999)}.txt"
        
        try:
            upload_headers = self.headers.copy()
            upload_headers["Content-Type"] = "text/plain"
            
            r_upload = requests.post(
                f"{self.url}/storage/v1/object/{bucket_name}/{test_file}",
                headers=upload_headers,
                data=test_content
            )
            
            if r_upload.status_code == 200 or r_upload.status_code == 201:
                print(f"[!] Can upload files to {bucket_name}")
                self.findings.append({
                    'severity': 'HIGH',
                    'finding': f'Unrestricted upload: {bucket_name}',
                    'detail': f'Can upload files to public bucket'
                })
                
                # Try to download the uploaded file
                dl = requests.get(
                    f"{self.url}/storage/v1/object/public/{bucket_name}/{test_file}",
                    headers=self.headers
                )
                if dl.status_code == 200:
                    print(f"[!] Can download uploaded file (public access)")
                    self.findings.append({
                        'severity': 'MEDIUM',
                        'finding': f'Public file access: {bucket_name}',
                        'detail': f'Uploaded files are publicly accessible'
                    })
            else:
                print(f"[-] Upload denied: {r_upload.status_code}")
        except Exception as e:
            print(f"[-] Upload test failed: {e}")
        
        return results
    
    def check_bucket_policies(self, bucket):
        """Check bucket policies"""
        bucket_id = bucket.get('id')
        bucket_name = bucket.get('name')
        
        # Try to get policy information
        try:
            r = requests.get(
                f"{self.url}/storage/v1/bucket/{bucket_id}/policy",
                headers=self.headers
            )
            
            if r.status_code == 200:
                policy = r.json()
                print(f"[*] Policy found for {bucket_name}")
                return policy
        except:
            pass
        
        return None
    
    def run(self):
        """Run full storage audit"""
        print("="*60)
        print("JERICHO SUPABASE STORAGE AUDITOR")
        print("="*60)
        
        self.list_buckets()
        
        if not self.buckets:
            print("[-] No buckets found")
            return
        
        print(f"\n[*] Auditing {len(self.buckets)} buckets...")
        for bucket in self.buckets:
            bucket_name = bucket.get('name')
            if bucket_name:
                self.test_bucket_access(bucket_name)
                self.check_bucket_policies(bucket)
        
        print("\n" + "="*60)
        print("STORAGE AUDIT SUMMARY")
        print("="*60)
        
        if self.findings:
            print(f"[!] Found {len(self.findings)} issues:")
            for finding in self.findings:
                print(f"[{finding['severity']}] {finding['finding']}")
                print(f"    {finding['detail']}\n")
        else:
            print("[+] No storage misconfigurations found")
        
        # Save results
        with open('storage_audit.json', 'w') as f:
            json.dump({
                'buckets': self.buckets,
                'findings': self.findings
            }, f, indent=2)
        print("[*] Results saved to storage_audit.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Storage Auditor")
    parser.add_argument("-u", "--url", required=True, help="Supabase project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon key")
    args = parser.parse_args()
    
    auditor = StorageAuditor(args.url, args.key)
    auditor.run()

if __name__ == "__main__":
    main()
