# Supabase Security Assessment Arsenal: Engineering Manual

A modular offensive framework for auditing Supabase-backed architectures. This suite identifies misconfigurations in PostgREST, RLS policies, and Storage buckets by systematically exercising the Trust Boundary.

## Assessment Methodology: The Escalation Chain
1. **Enumeration**: Extract schema and API surface via OpenAPI specification.
2. **Access Probing**: Validate table/bucket permissions against the `anon` key.
3. **Logic Testing**: Execute authenticated requests to detect IDOR and flawed RLS policy logic.
4. **Credential Harvesting**: Analyze client-side bundles for `service_role` keys or JWT secrets.

## Module Engineering Details

### 1. reconnaissance/project_mapper.py
* **Why**: The API surface is often undocumented. We must map the schema to define the attack surface.
* **How**: Queries the root PostgREST endpoint to dump the OpenAPI specification, identifying all accessible tables, RPC functions, and storage buckets.

### 2. auth/auth_audit.py
* **Why**: Auth misconfigurations are the entry point for session manipulation.
* **How**: Tests for insecure email verification flows, open redirects in OAuth callbacks, and verifies if the project allows unauthenticated sign-ups.

### 3. database/rls_audit.py
* **Why**: RLS is the final security boundary. Flawed policies (e.g., using `auth.role() = 'authenticated'` without ownership checks) are the primary source of data breaches.
* **How**: Iterates through all public tables, attempting `SELECT/INSERT/UPDATE` operations with both `anon` and `authenticated` JWTs to detect horizontal/vertical privilege escalation.

### 4. database/schema_enum.py
* **Why**: Understanding data relationships is required to identify sensitive columns (e.g., `api_key`, `token`, `password`).
* **How**: Performs a full schema dump including column types, foreign key relationships, and identifying high-value data patterns.

### 5. database/function_audit.py
* **Why**: RPC functions often run with elevated `SECURITY DEFINER` privileges, bypassing standard RLS.
* **How**: Probes the `/rpc/` endpoint, testing functions with various parameter fuzzing to detect injection and data exposure.

### 6. storage/bucket_audit.py
* **Why**: Storage is often overlooked. Public buckets can expose backups, PII, or configuration files.
* **How**: Automates listing, reading, and writing attempts against all identified buckets to verify bucket-level access control.

### 7. realtime/channel_audit.py
* **Why**: WebSockets (Realtime) are prone to data leakage if channel subscriptions aren't restricted by RLS.
* **How**: Attempts to subscribe to public and private channels to observe if data is broadcasted without authorization.

### 8. secrets/key_exposure.py
* **Why**: Finding a `service_role` key in frontend code is a critical vulnerability.
* **How**: Crawls target application JS bundles for patterns matching Supabase keys, JWT secrets, and environment variable patterns.

### 9. report/findings.py
* **Why**: Documentation is as important as exploitation for remediation tracking.
* **How**: Aggregates all JSON outputs into a unified report with severity ratings (CRITICAL/HIGH/MEDIUM/LOW).

## Execution Orchestration
The `supabase_arsenal.py` script serves as the master orchestrator.

### Full Assessment
```bash
python3 supabase_arsenal.py -u <PROJECT_URL> -k <ANON_KEY> -a <AUTH_JWT>
Module-Specific Auditing
Bash
# Run RLS audit exclusively
python3 supabase_arsenal.py -u <PROJECT_URL> -k <ANON_KEY> -m rls
Jericho: Serverless infrastructure auditing.
