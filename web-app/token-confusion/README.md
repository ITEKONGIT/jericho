# Token Confusion

Token confusion happens when a backend accepts a token for a purpose, audience, issuer, tenant, or privilege level it was not meant for. The token may be cryptographically valid, but it is valid for the wrong thing.

## Common Patterns

* `id_token` accepted as an API `access_token`.
* Refresh token accepted where an access token is required.
* Password reset token accepted as a session token.
* Email verification token accepted as authentication.
* Mobile token accepted by web APIs with different audience assumptions.
* Firebase, Supabase, Auth0, Cognito, or custom JWTs accepted interchangeably.
* Token from staging, dev, or another tenant accepted in production.
* API key treated as user identity rather than application identity.

## Why It Happens

Developers often validate only that a JWT is signed by a trusted key. That is not enough. A secure verifier must also validate:

* `iss`: who issued the token.
* `aud`: who the token is for.
* `exp` and `nbf`: whether the token is currently valid.
* `typ` or equivalent token purpose.
* `azp` or client id when relevant.
* Scopes and permissions.
* Tenant, organization, or project binding.
* Session version or revocation state for sensitive actions.

## Assessment Workflow

Compare how endpoints respond to different token classes:

* Valid access token for the target API.
* ID token for the same user.
* Refresh token for the same session.
* Expired token.
* Token from a different client app.
* Token from a different tenant or organization.
* Token from another environment.
* Low-privilege token.

Expected result: only the correct token type, issuer, audience, tenant, and scope should work.

## Detailed Things To Check

* Does the API accept an ID token because it only checks the signature?
* Does the API ignore `aud` and accept tokens issued for another service?
* Does the API accept tokens from another tenant with the same signing provider?
* Does role enforcement come from JWT claims that can become stale?
* Does logout or password reset revoke refresh tokens and bump session version?
* Does the gateway validate token claims differently from the application?
* Do WebSockets, file downloads, or background endpoints use weaker validation than REST?

## Developer Fix

* Use separate verifiers for access tokens, ID tokens, refresh tokens, reset tokens, and email verification tokens.
* Require the exact issuer and audience for each API.
* Reject unexpected token type or purpose.
* Bind tokens to tenant, client id, and session where applicable.
* Keep access tokens short-lived.
* Rotate and revoke refresh tokens.
* Re-check sensitive permissions server-side instead of relying only on long-lived JWT claims.
* Add tests that pass the wrong token type and expect rejection.

Use only on systems where you have authorization to test.
