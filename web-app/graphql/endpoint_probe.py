#!/usr/bin/env python3
import argparse
from urllib.parse import urljoin

import requests

COMMON_PATHS = (
    "/graphql",
    "/api/graphql",
    "/v1/graphql",
    "/query",
    "/graphiql",
    "/playground",
)


def parse_header(raw_header):
    if not raw_header:
        return {}
    if ":" not in raw_header:
        raise ValueError("Header must use 'Name: value' format.")
    name, value = raw_header.split(":", 1)
    return {name.strip(): value.strip()}


def probe_endpoint(url, headers, timeout):
    query = {"query": "query { __typename }"}
    try:
        response = requests.post(
            url,
            json=query,
            headers={"Content-Type": "application/json", **headers},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        return {"url": url, "error": str(exc)}

    result = {
        "url": url,
        "status": response.status_code,
        "content_type": response.headers.get("content-type", ""),
    }

    try:
        payload = response.json()
    except ValueError:
        result["graphql_like"] = False
        return result

    result["graphql_like"] = "data" in payload or "errors" in payload
    if payload.get("errors"):
        result["error_sample"] = payload["errors"][0].get("message", "Unknown error")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Placeholder GraphQL endpoint probe for authorized no-auth or low-auth checks."
    )
    parser.add_argument("-b", "--base-url", required=True, help="Base URL, for example https://target.example")
    parser.add_argument(
        "-H",
        "--header",
        help="Optional single low-privilege header, for example 'Authorization: Bearer token'",
    )
    parser.add_argument("--timeout", type=int, default=8, help="Request timeout in seconds")
    args = parser.parse_args()

    headers = parse_header(args.header)
    base = args.base_url.rstrip("/") + "/"

    print("[*] Probing common GraphQL paths with a read-only __typename query.\n")
    for path in COMMON_PATHS:
        url = urljoin(base, path.lstrip("/"))
        result = probe_endpoint(url, headers, args.timeout)

        if result.get("error"):
            print(f"[-] {url} -> request failed: {result['error']}")
            continue

        marker = "+" if result.get("graphql_like") else "-"
        print(
            f"[{marker}] {url} -> {result['status']} "
            f"{result.get('content_type', '').split(';')[0]}"
        )
        if result.get("error_sample"):
            print(f"    error: {result['error_sample']}")


if __name__ == "__main__":
    main()
