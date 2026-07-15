#!/usr/bin/env python3
"""
Jericho Supabase Key Exposure Scanner
Checks for exposed Supabase keys in frontend and source code
"""

import requests
import json
import argparse
import sys
import re
from urllib.parse import urlparse, parse_qs

class KeyExposureScanner:
    def __init__(self, target_url, anon_key=None):
        self.target_url = target_url.rstrip('/')
        self.anon_key = anon_key
        self.findings = []
        self.patterns = {
            'supabase_url': re.compile(r'https?://[a-zA-Z0-9-]+\.supabase\.co'),
            'anon_key': re.compile(r'[a-zA-Z0-9_-]{30,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}'),
            'service_key': re.compile(r'service_role\s*[:=]\s*[a-zA-Z0-9_-]{30,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}', re.I),
            'jwt_secret': re.compile(r'JWT_SECRET\s*[:=]\s*[a-zA-Z0-9_-]{30,}', re.I),
            'supabase_key': re.compile(r'(NEXT_PUBLIC_SUPABASE|REACT_APP_SUPABASE|VITE_SUPABASE|SUPABASE)[_\s]*[A-Z_]*KEY\s*[:=]\s*[a-zA-Z0-9_-]{30,}', re.I)
        }
    
    def scan_page(self, url, content):
        """Scan a single page for exposed keys"""
        print(f"[*] Scanning: {url}")
        
        findings = []
        
        # Check for Supabase URL
        supabase_urls = self.patterns['supabase_url'].findall(content)
        if supabase_urls:
            print(f"[+] Found Supabase URL: {supabase_urls[0]}")
            findings.append({
                'type': 'supabase_url',
                'value': supabase_urls[0],
                'url': url
            })
        
        # Check for JWT tokens
        tokens = self.patterns['anon_key'].findall(content)
        for token in tokens:
            # Check if it's likely a Supabase token
            if token.startswith('eyJ') and len(token) > 50:
                print(f"[!] Found JWT token: {token[:30]}...")
                findings.append({
                    'type': 'jwt_token',
                    'value': token,
                    'url': url,
                    'severity': 'HIGH'
                })
                
                # Check if it's a service_role key
                if 'service_role' in content.lower():
                    print("[CRITICAL] Found service_role key!")
                    findings.append({
                        'type': 'service_role_key',
                        'value': token,
                        'url': url,
                        'severity': 'CRITICAL'
                    })
        
        # Look for Supabase configuration
        config_patterns = [
            (r'NEXT_PUBLIC_SUPABASE_URL\s*[:=]\s*["\']([^"\']+)["\']', 'NEXT_PUBLIC_SUPABASE_URL'),
            (r'NEXT_PUBLIC_SUPABASE_ANON_KEY\s*[:=]\s*["\']([^"\']+)["\']', 'NEXT_PUBLIC_SUPABASE_ANON_KEY'),
            (r'REACT_APP_SUPABASE_URL\s*[:=]\s*["\']([^"\']+)["\']', 'REACT_APP_SUPABASE_URL'),
            (r'REACT_APP_SUPABASE_ANON_KEY\s*[:=]\s*["\']([^"\']+)["\']', 'REACT_APP_SUPABASE_ANON_KEY'),
            (r'VITE_SUPABASE_URL\s*[:=]\s*["\']([^"\']+)["\']', 'VITE_SUPABASE_URL'),
            (r'VITE_SUPABASE_ANON_KEY\s*[:=]\s*["\']([^"\']+)["\']', 'VITE_SUPABASE_ANON_KEY'),
        ]
        
        for pattern, name in config_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                print(f"[!] Found {name}: {match[:30]}...")
                findings.append({
                    'type': name,
                    'value': match,
                    'url': url,
                    'severity': 'MEDIUM' if 'anon' in name else 'HIGH'
                })
        
        return findings
    
    def crawl_site(self, url):
        """Crawl a site for exposed keys"""
        print(f"[*] Crawling: {url}")
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                content = response.text
                findings = self.scan_page(url, content)
                self.findings.extend(findings)
                
                # Look for JS files
                js_files = re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', content)
                for js_file in js_files:
                    if js_file.startswith('http'):
                        js_url = js_file
                    else:
                        js_url = urlparse.urljoin(url, js_file)
                    
                    try:
                        js_response = requests.get(js_url, timeout=10, verify=False)
                        if js_response.status_code == 200:
                            js_findings = self.scan_page(js_url, js_response.text)
                            self.findings.extend(js_findings)
                    except:
                        pass
            else:
                print(f"[-] Failed to fetch {url}: {response.status_code}")
        except Exception as e:
            print(f"[-] Error crawling {url}: {e}")
    
    def run(self):
        """Run the scanner"""
        print("="*60)
        print("JERICHO SUPABASE KEY EXPOSURE SCANNER")
        print("="*60)
        
        # Scan the target URL
        self.crawl_site(self.target_url)
        
        # Summary
        print("\n" + "="*60)
        print("SCAN SUMMARY")
        print("="*60)
        print(f"Total findings: {len(self.findings)}")
        
        critical = [f for f in self.findings if f.get('severity') == 'CRITICAL']
        high = [f for f in self.findings if f.get('severity') == 'HIGH']
        
        if critical:
            print(f"[CRITICAL] Found {len(critical)} critical issues:")
            for finding in critical:
                print(f"    - {finding['type']}: {finding['value'][:30]}...")
        
        if high:
            print(f"[HIGH] Found {len(high)} high-risk issues:")
            for finding in high:
                print(f"    - {finding['type']}: {finding['value'][:30]}...")
        
        # Save results
        with open('key_exposure.json', 'w') as f:
            json.dump({
                'target': self.target_url,
                'findings': self.findings
            }, f, indent=2)
        print("[*] Results saved to key_exposure.json")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase Key Exposure Scanner")
    parser.add_argument("-u", "--url", required=True, help="Target URL to scan")
    args = parser.parse_args()
    
    scanner = KeyExposureScanner(args.url)
    scanner.run()

if __name__ == "__main__":
    main()
