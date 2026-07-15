#!/usr/bin/env python3
import requests, argparse, sys

def audit_rls(url, anon_key, table):
    headers = {"apikey": anon_key, "Authorization": f"Bearer {anon_key}"}
    print(f"[*] Probing table: {table}")
    
    # Test Read
    r = requests.get(f"{url}/rest/v1/{table}?select=*", headers=headers)
    if r.status_code == 200:
        if r.json():
            print(f"[!] VULNERABLE: Data leaked from {table}!")
        else:
            print(f"[-] Table {table} is empty or protected.")
    else:
        print(f"[-] {table} Access Denied: {r.status_code}")

def main():
    parser = argparse.ArgumentParser(description="Jericho Supabase RLS Auditor")
    parser.add_argument("-u", "--url", required=True, help="Project URL")
    parser.add_argument("-k", "--key", required=True, help="Anon Key")
    parser.add_argument("-t", "--table", required=True, help="Table to probe")
    args = parser.parse_args()

    audit_rls(args.url, args.key, args.table)

if __name__ == "__main__":
    main()
