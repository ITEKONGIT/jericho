# Source Map Leakage

Source maps often expose the original frontend source behind production bundles. They can reveal routes, API endpoints, feature flags, auth logic, comments, test code, environment names, and frontend encryption material.

## What To Look For

Common files:

```text
/static/js/main.js.map
/assets/index.js.map
/_next/static/chunks/*.js.map
/build/*.map
/dist/*.map
```

Also inspect JavaScript bundles for a footer like:

```text
//# sourceMappingURL=main.js.map
```

## Useful Findings

Source maps can expose:

* Original route names and hidden pages.
* API base URLs and internal endpoint paths.
* GraphQL queries and mutations.
* tRPC or RPC method names.
* Auth guards and role checks.
* Feature flag names.
* Frontend encryption keys, salts, KDF parameters, and request wrappers.
* Backend-issued key renewal endpoints.
* Comments that mention internal assumptions or temporary bypasses.
* Cloud project ids, Firebase/Supabase config, Sentry DSNs, and analytics tokens.

## Assessment Workflow

1. Inventory all loaded JavaScript files from DevTools Network.
2. Check each bundle for `sourceMappingURL`.
3. Request the `.map` file directly.
4. Search recovered sources for auth, reset, token, tenant, org, role, crypto, GraphQL, and API names.
5. Use the discovered routes and endpoints to guide authorized API testing.

## Developer Fix

* Do not publish production source maps publicly.
* Upload source maps privately to error tracking systems when needed.
* Strip secrets, comments, and internal-only config from frontend builds.
* Treat frontend code as public even when source maps are disabled.
* Monitor for `.map` files in release pipelines and CDN artifacts.

Use only on systems where you have authorization to test.
