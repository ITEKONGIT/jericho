# WEB-APP Security
Payloads and automation scripts for web application testing.

- **auth-endpoints/**: Checks for endpoints that still work after auth headers, cookies, API keys, or JWT claims are removed or tampered.
- **cache-invalidation/**: Methodology and developer fixes for token/JWT-tied cache exposure after logout.
- **graphql/**: Placeholder GraphQL enumeration helpers for no-auth or explicitly low-privilege introspection checks.
- **password-reset/**: Detailed assessment notes for OTP weakness, identity binding, reset response leakage, and session invalidation.
- **source-maps/**: Source map leakage workflow for recovering frontend routes, auth logic, API paths, and encryption material.
- **token-confusion/**: Token purpose, audience, issuer, tenant, and privilege confusion checks with developer fixes.
- **turbo-intruder/**: Pre-configured Python scripts for advanced rate-limit testing, OTP brute-forcing, and high-concurrency fuzzing via Burp Suite.
