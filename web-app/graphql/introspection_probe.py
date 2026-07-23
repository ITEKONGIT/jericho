#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

import requests

INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      kind
      name
      fields(includeDeprecated: true) {
        name
        args {
          name
          type { kind name ofType { kind name } }
        }
        type { kind name ofType { kind name } }
        isDeprecated
        deprecationReason
      }
    }
  }
}
"""


def parse_header(raw_header):
    if not raw_header:
        return {}
    if ":" not in raw_header:
        raise ValueError("Header must use 'Name: value' format.")
    name, value = raw_header.split(":", 1)
    return {name.strip(): value.strip()}


def post_graphql(url, query, headers, timeout):
    response = requests.post(
        url,
        json={"query": query},
        headers={"Content-Type": "application/json", **headers},
        timeout=timeout,
    )
    return response


def print_section(title):
    print(f"\n{'=' * 60}\n[*] {title}\n{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(
        description="Read-only GraphQL introspection probe for authorized assessments."
    )
    parser.add_argument("-u", "--url", required=True, help="GraphQL endpoint URL")
    parser.add_argument(
        "-H",
        "--header",
        help="Optional single low-privilege header, for example 'Authorization: Bearer token'",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="graphql_schema.json",
        help="Output path for introspection JSON",
    )
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()

    try:
        headers = parse_header(args.header)
    except ValueError as exc:
        print(f"[-] {exc}")
        sys.exit(2)

    print_section("GraphQL Endpoint Health")
    try:
        health = post_graphql(args.url, "query { __typename }", headers, args.timeout)
    except requests.RequestException as exc:
        print(f"[-] Request failed: {exc}")
        sys.exit(1)

    print(f"[*] Status: {health.status_code}")
    if health.headers.get("content-type"):
        print(f"[*] Content-Type: {health.headers.get('content-type')}")

    if health.status_code >= 500:
        print("[!] Server error returned during minimal GraphQL probe.")
    elif health.status_code in (401, 403):
        print("[-] Endpoint requires authentication for minimal queries.")
    elif health.ok:
        print("[+] Endpoint responded to a minimal GraphQL query.")
    else:
        print("[?] Endpoint responded, but not with a clear success status.")

    print_section("Standard Introspection")
    try:
        introspection = post_graphql(args.url, INTROSPECTION_QUERY, headers, args.timeout)
    except requests.RequestException as exc:
        print(f"[-] Introspection request failed: {exc}")
        sys.exit(1)

    print(f"[*] Status: {introspection.status_code}")
    try:
        payload = introspection.json()
    except ValueError:
        print("[-] Response was not JSON.")
        sys.exit(1)

    if payload.get("errors"):
        print("[-] Introspection returned errors:")
        for error in payload["errors"][:5]:
            print(f"    - {error.get('message', 'Unknown error')}")
        sys.exit(0)

    schema = payload.get("data", {}).get("__schema")
    if not schema:
        print("[-] No __schema object returned.")
        sys.exit(0)

    output = Path(args.output)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    query_type = schema.get("queryType", {}).get("name")
    mutation_type = schema.get("mutationType", {}) or {}
    type_count = len(schema.get("types", []))

    print("[+] Introspection is enabled for this request context.")
    print(f"[*] Query type: {query_type or 'unknown'}")
    print(f"[*] Mutation type: {mutation_type.get('name') or 'none exposed'}")
    print(f"[*] Type count: {type_count}")
    print(f"[*] Schema written to: {output}")


if __name__ == "__main__":
    main()
