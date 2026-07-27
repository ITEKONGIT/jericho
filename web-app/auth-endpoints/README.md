# Auth Endpoint Assumptions

Some endpoints are built with auth headers, API keys, or bearer tokens in normal client traffic, but the backend does not actually require them. This happens when authorization is enforced in frontend logic, API gateway rules are incomplete, or controller-level checks are missing.

## No-Auth Replay

For authorized testing, compare the same request in multiple states:

* Normal authenticated request.
* Same request with `Authorization` removed.
* Same request with cookies removed.
* Same request with API key removed.
* Same request with a malformed token.
* Same request with an expired token.
* Same request with another low-privilege user's token.

Watch for:

* `200 OK` without auth.
* Different data but still successful behavior.
* Mutations that work without auth.
* Public API keys being treated as user authorization.
* Backend using only `user_id`, `org_id`, or `tenant_id` from the body.

## JWT Value Tampering

Changing JWT values is useful for checking whether the backend verifies signatures, issuer, audience, token type, and authorization context.

Check carefully:

* Change `sub`, `user_id`, `role`, `tenant_id`, `org_id`, `scope`, or `email`.
* Change `alg` only to confirm insecure acceptance is not present.
* Replay a token from another tenant or environment.
* Send a validly structured but unsigned or wrongly signed token.
* Send a token with a valid signature but wrong audience or issuer.

Secure backends must reject tampered JWTs because the signature no longer matches. If changed claims are accepted, the server is trusting decoded JWT content without proper validation.

## Developer Fix

* Enforce auth server-side on every protected endpoint.
* Treat frontend checks as usability only, never authorization.
* Validate JWT signature, algorithm allowlist, issuer, audience, expiry, not-before, and token type.
* Resolve authorization from trusted server-side policy, not body fields.
* Use object-level authorization for every user, tenant, project, and workspace id.
* Test endpoints with auth removed as part of CI or security regression checks.

Use only on systems where you have authorization to test.
