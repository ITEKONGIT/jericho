# Token Cache Invalidation

Many apps cache user data against a JWT, access token, session id, or derived cache key. If logout only clears the browser state but does not invalidate server-side cache entries or token authority, the last token can still retrieve sensitive cached data until token expiry or cache eviction.

## What To Check

* Log in and request user-specific data such as profile, billing, messages, or dashboard state.
* Capture the access token or session-bearing request in an intercepting proxy.
* Log out through the normal UI.
* Replay the captured request with the old token.
* Confirm whether fresh data, cached data, or stale personalized responses are still returned.

High-risk signs:

* Logout does not rotate or revoke refresh tokens.
* API gateways or CDNs cache authenticated responses.
* Cache keys include only the token string, user id, or URL path.
* `Authorization`, `Cookie`, or tenant headers are missing from `Vary`.
* Personalized responses use `Cache-Control: public` or long `max-age`.
* Backend accepts JWTs until expiry with no revocation/version check.

## Impact

This creates post-logout data exposure. A token copied from logs, browser storage, mobile storage, proxy history, or a compromised device can continue pulling data even after the user believes the session is closed.

## Developer Fix

Use more than client-side logout:

* Keep access tokens short-lived.
* Rotate refresh tokens on every use and revoke them on logout.
* Store a server-side session version, token version, or `jti` denylist and check it for sensitive endpoints.
* Purge user/session cache entries during logout and password reset.
* Never share cache entries across users, tenants, scopes, or authorization states.
* For authenticated responses, prefer `Cache-Control: private, no-store` unless caching is explicitly safe.
* If caching is needed, key by user id, tenant id, scopes, session version, and authorization context.
* Configure `Vary: Authorization, Cookie` where intermediaries may cache responses.

## Safe Pattern

```text
cache_key = user_id + tenant_id + scopes_hash + session_version + request_fingerprint
```

On logout, increment or revoke the session version, reject old refresh tokens, and delete cache entries tied to the previous version. Password reset and account disable events should perform the same invalidation.

Use only on systems where you have authorization to test.
