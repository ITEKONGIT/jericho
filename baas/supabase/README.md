# 🔍 Jericho Supabase Security Assessment Arsenal

## 📖 Executive Summary

The Supabase Security Assessment Arsenal represents a complete offensive security framework for evaluating Supabase-backed applications. Built on the Jericho "Platform-as-a-Library" philosophy, this arsenal transforms isolated security checks into a unified, repeatable, and methodology-driven assessment pipeline.

Supabase has emerged as one of the most popular open-source Firebase alternatives, offering a PostgreSQL-based backend with automatic REST and GraphQL APIs, realtime subscriptions, storage, and authentication. However, its developer-friendly defaults often lead to critical security misconfigurations that are exploitable via the public `anon` key that is intentionally embedded in frontend applications.

**This arsenal systematically identifies, tests, and documents vulnerabilities across the entire Supabase attack surface.**

---

## 🧠 The Jericho Supabase Philosophy

### The Trust Boundary Model

Supabase architecture follows a clear trust boundary model that defines our assessment strategy:
┌─────────────────────────────────────────────────────────────┐
│ CLIENT (Untrusted) │
│ - Browser/ Mobile App / Frontend │
│ - Contains: anon key (public), user JWT tokens │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ SUPABASE API LAYER │
│ - PostgREST (REST API) │
│ - Realtime (WebSockets) │
│ - Storage (S3-compatible) │
│ - Auth (JWT-based) │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ POSTGRESQL (Trusted) │
│ - Row Level Security (RLS) - The final auth boundary │
│ - Database functions (RPC) │
│ - Views, triggers, stored procedures │
└─────────────────────────────────────────────────────────────┘

text

### The Assessment Question Set

Every component is assessed against four fundamental questions:

| Layer | Question | What It Reveals |
|-------|----------|-----------------|
| **Identity** | "Who does Supabase think the user is?" | Auth configuration, providers, MFA, session handling |
| **Role** | "What can the anon role actually do?" | RLS misconfigurations, policy gaps |
| **Authorization** | "Can User A access User B's data?" | Broken ownership enforcement, IDOR |
| **Exposure** | "What database objects are accidentally exposed?" | Schema enumeration, function abuse |

### The "Anonymous Role" Fallacy

**The critical insight:** Supabase intentionally exposes the `anon` key in frontend code. This is by design. The security model assumes the `anon` role should be untrusted. The assessment asks: *"What can the anon role actually do that it shouldn't?"*

Common misconfigurations:
- **RLS disabled**: Entire tables readable/writable by anyone
- **Weak policies**: `auth.role() = 'authenticated'` without ownership checks
- **Service role exposure**: The `service_role` key (bypasses all RLS) found in frontend code

---

## 🏗️ Arsenal Architecture

The arsenal is organized to follow the Supabase attack surface systematically:
supabase/
│
├── supabase_arsenal.py # Master orchestrator
│
├── reconnaissance/ # Discovery phase
│ └── project_mapper.py # Auto-discover tables, functions, buckets
│
├── auth/ # Identity & auth layer
│ └── auth_audit.py # OAuth providers, verification, MFA
│
├── database/ # PostgreSQL layer
│ ├── rls_audit.py # Row Level Security testing
│ ├── schema_enum.py # Complete schema enumeration
│ └── function_audit.py # RPC function security analysis
│
├── storage/ # Object storage layer
│ └── bucket_audit.py # Bucket permissions, public access
│
├── realtime/ # WebSocket layer
│ └── channel_audit.py # Channel subscription security
│
├── secrets/ # Key exposure scanning
│ └── key_exposure.py # Frontend/JS key harvesting
│
└── report/ # Output generation
└── findings.py # Unified HTML/JSON report

text

---

## 📋 Module Deep-Dive

### 1. reconnaissance/project_mapper.py
**Purpose:** Discover the entire attack surface without prior knowledge.

**Why it exists:** Attackers need to know what tables exist before testing them. This module leverages the auto-generated OpenAPI specification to discover all exposed database objects.

**What it tests:**
- Exposed tables and views
- RPC functions
- Storage buckets
- Schema structure (column names, types)

**Attack surface identified:**
- Tables that shouldn't be public
- Functions that expose internal logic
- Buckets with listing permissions

**Usage:**
```bash
python3 reconnaissance/project_mapper.py -u "https://project-ref.supabase.co" -k "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Required parameters:

-u, --url: The Supabase project URL (e.g., https://xyz.supabase.co)

-k, --key: The public anon key (found in frontend source)

What the parameters mean:

The URL defines the attack target

The anon key provides the API access level being tested

Together they define what resources are accessible to an untrusted client

Output: recon_results.json - Full list of discovered objects

2. auth/auth_audit.py
Purpose: Test authentication configuration and provider security.

Why it exists: Authentication is the first trust boundary. Misconfigurations here can lead to account takeover, unauthorized access, or information disclosure.

What it tests:

Email verification requirements

OAuth provider configurations

Redirect URL validation (open redirect)

MFA availability

Session configuration

Attack vectors tested:

Sign-up without email confirmation

OAuth redirect manipulation

Provider enumeration (Google, GitHub, etc.)

Usage:

bash
python3 auth/auth_audit.py -u "https://project-ref.supabase.co" -k "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key for API access

Output: auth_findings.json - Authentication weaknesses identified

3. database/rls_audit.py
Purpose: Test Row Level Security policies on every exposed table.

Why it exists: RLS is the primary security boundary in Supabase. The entire data protection model relies on properly configured policies. This is the most critical module.

What it tests:

READ access: Can the anon role SELECT from tables?

WRITE access: Can the anon role INSERT/UPDATE/DELETE?

Authenticated access: What can authenticated users access?

Ownership enforcement: Can users access data belonging to others?

Understanding the tests:

Test	What It Checks	What It Means
SELECT with anon key	"Can anyone read this table?"	If yes, sensitive data is exposed
INSERT with anon key	"Can anyone insert into this table?"	If yes, data injection is possible
SELECT with auth token	"What can authenticated users read?"	May reveal horizontal privilege escalation
Ownership testing	"Can User A read User B's data?"	IDOR vulnerability
Usage:

bash
# Basic test with only anon key
python3 database/rls_audit.py -u "https://project-ref.supabase.co" -k "ANON_KEY"

# Test authenticated policies as well
python3 database/rls_audit.py -u "https://project-ref.supabase.co" -k "ANON_KEY" -a "AUTH_JWT_TOKEN"
Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key

-a, --auth: (Optional) Authenticated JWT token - critical for testing logged-in user privileges

What the JWT token gives you:

Testing with a valid JWT allows testing policies that require auth.uid() = user_id

Reveals if authenticated users can access other users' data

Tests if administrators can be impersonated

Output: rls_audit_results.json - Complete RLS audit with severity ratings

4. database/schema_enum.py
Purpose: Enumerate complete database schema including columns, relationships, and sensitive data patterns.

Why it exists: Understanding schema structure reveals sensitive columns, potential injection points, and data relationships.

What it enumerates:

All tables in the public schema

Column names and data types

Primary/foreign key relationships

Sensitive columns (password, token, api_key, etc.)

Usage:

bash
python3 database/schema_enum.py -u "https://project-ref.supabase.co" -k "ANON_KEY"

# If you have service_role key (bypasses all RLS)
python3 database/schema_enum.py -u "https://project-ref.supabase.co" -k "SERVICE_ROLE_KEY" --service-role
Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key

--service-role: Flag indicating the key is a service_role key (bypasses RLS)

What the service_role flag means:

The service_role key bypasses all RLS policies

It's intended for backend servers only

Finding this exposed is CRITICAL - complete database compromise

Output: schema_enumeration.json - Full schema with columns and sample data

5. database/function_audit.py
Purpose: Audit RPC functions for privilege escalation, injection, and data exposure.

Why it exists: PostgreSQL functions (/rpc/*) can execute arbitrary database logic. Functions declared with SECURITY DEFINER run with elevated privileges.

What it tests:

Function accessibility with empty parameters

Function behavior with various parameter inputs

Sensitive function identification (admin, config, exec, etc.)

Data return analysis (what does the function expose?)

Common attack patterns:

Privilege escalation: Function runs with higher privileges than user

Information disclosure: Function returns sensitive data

Parameter injection: Function accepts unsafe parameters

Function chaining: Can call one function to enable another

Usage:

bash
python3 database/function_audit.py -u "https://project-ref.supabase.co" -k "ANON_KEY"
Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key

Output: function_audit.json - Accessible functions and their responses

6. storage/bucket_audit.py
Purpose: Test storage bucket security and object permissions.

Why it exists: Storage is often overlooked. Public buckets can expose sensitive files, documents, backups, and even executable code.

What it tests:

Bucket listing permissions

Object read/upload/delete capabilities

Public vs private bucket status

File overwrite permissions

Uploaded file accessibility

Attack vectors:

Data exposure: Public buckets with sensitive files

Malicious upload: Upload arbitrary files (phishing, malware)

File overwrite: Overwrite existing files (defacement, backdoor)

Mass enumeration: List all objects in a bucket

Usage:

bash
python3 storage/bucket_audit.py -u "https://project-ref.supabase.co" -k "ANON_KEY"
Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key

Output: storage_audit.json - Bucket access findings

7. realtime/channel_audit.py
Purpose: Test realtime WebSocket channel security.

Why it exists: Realtime subscriptions can leak sensitive data if channels are misconfigured. Unauthorized users might subscribe to private channels.

What it tests:

Realtime service availability

Public channel access

Authentication requirements

Channel subscription permissions

Usage:

bash
python3 realtime/channel_audit.py -u "https://project-ref.supabase.co" -k "ANON_KEY"
Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key

Output: realtime_audit.json - Realtime security findings

8. secrets/key_exposure.py
Purpose: Scan frontend code for exposed Supabase keys.

Why it exists: The service_role key or JWT secret should never be in frontend code. This module crawls target applications to find exposed credentials.

What it scans for:

anon keys (expected, but part of the chain)

service_role keys (CRITICAL - immediate compromise)

JWT secrets (CRITICAL - token forging possible)

Environment variables

Configuration in JS bundles

Usage:

bash
python3 secrets/key_exposure.py -u "https://target-application.com"
Required parameters:

-u, --url: Target application URL to crawl (not the Supabase URL)

Output: key_exposure.json - Found keys with severity ratings

9. report/findings.py
Purpose: Aggregate all audit results into a comprehensive HTML report.

Why it exists: Documentation is critical. This module creates a professional report that can be shared with stakeholders, clients, or used for remediation tracking.

Usage:

bash
python3 report/findings.py
Output: supabase_report.html - Complete audit report with severity breakdown

10. supabase_arsenal.py
Purpose: Master orchestrator - runs all modules and generates a unified report.

Why it exists: Efficiency. Running a complete assessment should be a single command. This orchestrator manages dependencies, sequences modules appropriately, and handles errors.

Usage:

bash
# Run full assessment
python3 supabase_arsenal.py -u "https://project-ref.supabase.co" -k "ANON_KEY"

# Run full assessment with authenticated JWT
python3 supabase_arsenal.py -u "https://project-ref.supabase.co" -k "ANON_KEY" -a "AUTH_JWT"

# Run a single module
python3 supabase_arsenal.py -u "https://project-ref.supabase.co" -k "ANON_KEY" -m rls
Module names for single execution:

project_mapper - Discover attack surface

auth - Test authentication

rls - Test RLS policies

schema - Enumerate schema

functions - Audit RPC functions

storage - Test bucket security

realtime - Test realtime security

secrets - Scan for key exposure

report - Generate report

Required parameters:

-u, --url: Supabase project URL

-k, --key: Anon key

-a, --auth: (Optional) Authenticated JWT for authenticated testing

-m, --module: (Optional) Run a specific module only

🎯 Complete Assessment Workflow
Phase 1: Reconnaissance
bash
python3 reconnaissance/project_mapper.py -u "https://project.supabase.co" -k "ANON_KEY"
# Identifies all tables, functions, and buckets
Phase 2: Key Exposure (External)
bash
python3 secrets/key_exposure.py -u "https://target-application.com"
# Scans frontend for exposed keys and JWT tokens
Phase 3: Authentication Audit
bash
python3 auth/auth_audit.py -u "https://project.supabase.co" -k "ANON_KEY"
# Tests auth config, providers, verification
Phase 4: Database Security
bash
# 4a: Schema enumeration
python3 database/schema_enum.py -u "https://project.supabase.co" -k "ANON_KEY"

# 4b: RLS audit (critical)
python3 database/rls_audit.py -u "https://project.supabase.co" -k "ANON_KEY"

# 4c: Function audit
python3 database/function_audit.py -u "https://project.supabase.co" -k "ANON_KEY"
Phase 5: Storage Security
bash
python3 storage/bucket_audit.py -u "https://project.supabase.co" -k "ANON_KEY"
Phase 6: Realtime Security
bash
python3 realtime/channel_audit.py -u "https://project.supabase.co" -k "ANON_KEY"
Phase 7: Reporting
bash
python3 report/findings.py -o "supabase_assessment_report.html"
Phase 8: Full Orchestration
bash
python3 supabase_arsenal.py -u "https://project.supabase.co" -k "ANON_KEY" -a "AUTH_JWT"
🛡️ Finding Severity Matrix
Severity	Meaning	Example
CRITICAL	Immediate compromise risk	Service_role key exposure, RLS disabled on sensitive table
HIGH	Significant data breach potential	Public bucket with sensitive files, weak RLS policies
MEDIUM	Information disclosure	Schema enumeration, provider enumeration
LOW	Minimal risk	Missing security headers, verbose error messages
INFO	Informational	Enabled OAuth providers, discovered endpoints
🔬 Methodology References
The "Authenticated" Fallacy
A common vulnerability pattern: Developers implement a policy like:

sql
CREATE POLICY "Users can view data" ON users FOR SELECT USING (auth.role() = 'authenticated');
This is INSECURE. It only checks if the user is logged in, not if they own the data. The rls_audit.py module identifies these policies.

The "Missing RLS" Vulnerability
When RLS is disabled on a table, the anon key can perform any operation:

sql
-- Table: users, RLS: OFF
-- Anyone can:
SELECT * FROM users;  -- Dump all users
INSERT INTO users (email, password) VALUES ('attacker@example.com', 'hacked');
DELETE FROM users WHERE id = 1;
Service Role Key Compromise
The service_role key bypasses all RLS policies:

bash
# With service_role key, this works even if RLS would normally block it
curl -X GET "https://project.supabase.co/rest/v1/users?select=*" \
  -H "apikey: SERVICE_KEY" \
  -H "Authorization: Bearer SERVICE_KEY"
📊 Output Files Reference
Module	Output File	Contents
Project Mapper	recon_results.json	Discovered tables, functions, buckets
Auth Auditor	auth_findings.json	Auth configuration issues
RLS Auditor	rls_audit_results.json	RLS policy violations by table
Schema Enumerator	schema_enumeration.json	Complete table schemas
Function Auditor	function_audit.json	Accessible RPC functions
Storage Auditor	storage_audit.json	Bucket permissions
Realtime Auditor	realtime_audit.json	Channel security issues
Key Exposure Scanner	key_exposure.json	Exposed keys and tokens
Report Generator	supabase_report.html	Unified HTML report
🔧 Environment Setup
Dependencies
bash
pip install requests python-dateutil
Directory Structure
Ensure the following directories exist before running:

bash
mkdir -p reconnaissance auth database storage realtime secrets report
Permissions
bash
chmod +x supabase_arsenal.py
chmod +x */[!.]*.py
⚠️ Important Notes
Authorization Required: Only use these tools on targets you own or have explicit permission to test.

Rate Limiting: Supabase has rate limits. Use responsibly to avoid triggering protection mechanisms.

JWT Tokens: If you obtain an authenticated JWT, use it for testing. It reveals what authenticated users can access that anonymous users cannot.

Service Role Key: Finding a service_role key is a critical finding. It allows full database access bypassing all RLS.

Report Customization: The HTML report can be customized by modifying the template in report/findings.py.

🚀 Quick Start
bash
# 1. Navigate to the Supabase arsenal directory
cd ~/Desktop/jericho/baas/supabase

# 2. Run the full assessment
python3 supabase_arsenal.py \
  -u "https://your-project.supabase.co" \
  -k "YOUR_ANON_KEY" \
  -a "YOUR_AUTH_JWT"

# 3. Review the report
# Open supabase_report.html in your browser
📚 References
Supabase Documentation

PostgREST Documentation

Row Level Security

OWASP API Security Top 10

Jericho - And the walls came tumbling down.
