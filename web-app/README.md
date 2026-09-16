# WEB-APP Security
Payloads and automation scripts for web application testing.

## Newcomer ramp

**What this field is.** A web app is code running on a server I can only talk to through HTTP. Every check the developer wrote ("is this user an admin?") happens on that server — and every check the developer *skipped* is visible to me only if I ask the server directly, with requests the UI would never send.

**Why people miss findings here.** The tester sends the requests the app itself would send. The UI sends a valid access token — so token confusion never appears. The UI sends the auth header — so the endpoint that answers without it never appears. Logout is verified by the screen changing, not by replaying the request. The recurring miss: **taking the app's behavior as the server's contract.**

**Read order.** Start with [`auth-endpoints/`](auth-endpoints/) — it's the base assumption check (does the backend actually enforce anything?). Then [`token-confusion/`](token-confusion/) and [`cache-invalidation/`](cache-invalidation/) for the valid-token bug classes. [`password-reset/`](password-reset/) and [`source-maps/`](source-maps/) next. [`turbo-intruder/`](turbo-intruder/) when a finding needs proving at scale; [`graphql/`](graphql/) and [`apache-htaccess/`](apache-htaccess/) when the target has them. **Defer:** nothing here needs prior crypto or backend knowledge — HTTP + a proxy is the whole prerequisite.

- **apache-htaccess/**: Apache and `.htaccess` review for override scope, rewrite mistakes, directory listing, Basic Auth, handlers, and sensitive file exposure.
- **auth-endpoints/**: Checks for endpoints that still work after auth headers, cookies, API keys, or JWT claims are removed or tampered.
- **cache-invalidation/**: Methodology and developer fixes for token/JWT-tied cache exposure after logout.
- **graphql/**: Placeholder GraphQL enumeration helpers for no-auth or explicitly low-privilege introspection checks.
- **password-reset/**: Detailed assessment notes for OTP weakness, identity binding, reset response leakage, and session invalidation.
- **source-maps/**: Source map leakage workflow for recovering frontend routes, auth logic, API paths, and encryption material.
- **token-confusion/**: Token purpose, audience, issuer, tenant, and privilege confusion checks with developer fixes.
- **turbo-intruder/**: Pre-configured Python scripts for advanced rate-limit testing, OTP brute-forcing, and high-concurrency fuzzing via Burp Suite.
