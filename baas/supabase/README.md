JERICHO SUPABASE SECURITY ASSESSMENT ARSENAL
=============================================

EXECUTIVE SUMMARY
-----------------

The Supabase Security Assessment Arsenal is a complete offensive security framework for evaluating Supabase-backed applications. Built on the Jericho Platform-as-a-Library philosophy, this arsenal transforms isolated security checks into a unified, repeatable, and methodology-driven assessment pipeline.

Supabase is an open-source Firebase alternative offering a PostgreSQL-based backend with automatic REST and GraphQL APIs, realtime subscriptions, storage, and authentication. Its developer-friendly defaults often lead to critical security misconfigurations exploitable via the public anon key intentionally embedded in frontend applications.

This arsenal systematically identifies, tests, and documents vulnerabilities across the entire Supabase attack surface.

THE JERICHO SUPABASE PHILOSOPHY
-------------------------------

The Trust Boundary Model

Supabase architecture follows a clear trust boundary model that defines the assessment strategy. The client layer includes browser applications, mobile applications, third-party integrations, and contains the public anon key, user JWT tokens, and session data. This layer is considered completely untrusted with zero trust level.

The Supabase API layer consists of four components. PostgREST provides auto-generated REST endpoints for every table and view, OpenAPI specification generation, filtering and sorting support, pagination, and RPC function execution. Realtime provides WebSocket-based database change subscriptions, broadcast channels, presence tracking, and the WebSocket upgrade path. Storage provides S3-compatible object storage with file upload and download capabilities, bucket management, and CDN integration. Auth provides JWT-based authentication with email and password, OAuth providers, MFA factors, and admin operations.

The PostgreSQL layer represents the trusted database environment. Row Level Security functions as the final authority with per-table policies for INSERT, SELECT, UPDATE, and DELETE operations, policy expressions using auth.uid() and auth.role(), and bypass only possible with the service_role key. Database objects include tables, views, materialized views, functions, stored procedures, triggers, enums, domains, types, indices, constraints, and foreign keys. Extensions include pgcrypto for encryption, pgjwt for JWT handling, postgis for geospatial data, and vector for AI embeddings.

The Assessment Question Set

Every component is assessed against a comprehensive question matrix. The client layer asks what secrets are embedded in frontend code and what the security implication is for leaked service_role keys, JWT secrets, and API keys. The auth layer asks who Supabase thinks the user is and what the security implication is for identity spoofing, account takeover, and session hijacking. The PostgREST layer asks what the anon role can access and what the security implication is for data exposure and privilege escalation. The Realtime layer asks what channels unauthorized users can subscribe to and what the security implication is for data leakage via WebSockets and denial of service. The Storage layer asks what files users can list, read, upload, and delete and what the security implication is for data theft, malware hosting, and ransomware. The Database layer asks if User A can access User B's data and what the security implication is for IDOR and horizontal and vertical privilege escalation. The Functions layer asks if low-privilege users can execute high-privilege logic and what the security implication is for privilege escalation and remote code execution. The Schema layer asks what internal structures are accidentally exposed and what the security implication is for information disclosure for further attacks.

The Anonymous Role Fallacy

The critical insight is that Supabase intentionally exposes the anon key in frontend code by design. The security model assumes the anon role should be untrusted. The assessment asks what the anon role can actually do that it should not be able to do.

Understanding the Anon Key

The anon key is a JWT with the following characteristics. The subject is anon. The role is anon. The expiration is set to a far future date. The issued at timestamp is a standard Unix timestamp. Key properties include that it is public by design and intended to be in frontend code, the role is anon which identifies the user as unauthenticated, default permissions are restricted by RLS policies, and it never expires and is usually set to a distant future date.

What the anon key should be able to do includes signing up new users, signing in existing users, accessing publicly available data with proper RLS policies, and uploading to public buckets with proper policies.

What the anon key should not be able to do includes accessing sensitive tables such as users, profiles, and payments, modifying data without authorization, uploading to private buckets, and executing admin functions.

Finding the Anon Key in Frontend Code

React and Next.js applications typically store the Supabase URL and anon key in environment variables prefixed with NEXT_PUBLIC_. Vue and Vite applications use import.meta.env with VITE_ prefixes. Direct JavaScript implementations often hardcode the Supabase client initialization with the URL and key as string literals. Angular applications commonly define environment constants in environment.ts files. Mobile applications often hardcode the URL and key in configuration files or store them in platform-specific secure storage, though many developers mistakenly embed them directly in source code.

The Service Role Key

The service_role key is the polar opposite of the anon key. The subject is service_role. The role is service_role. The expiration is set to a far future date. The issued at timestamp is a standard Unix timestamp. Properties include that it is never exposed to clients and is intended for backend use only, the role is service_role which bypasses ALL RLS policies, it provides full database access for read, write, delete, and execute operations on everything, and it has escalated privileges that can perform any action in the project.

If found in frontend code, the finding is critical and indicates complete database compromise. An attacker can dump all tables including users, payments, and credentials, modify or delete any data, execute arbitrary SQL, and take over the entire project.

The Authenticated Fallacy

A common vulnerability pattern is often misunderstood. A vulnerable policy checks only the authenticated role without verifying ownership. This policy allows any authenticated user to access all records regardless of ownership.

Why this policy is vulnerable includes the following factors. The role check only verifies that the user is logged in without identifying which user is accessing the data, so any authenticated user can access the data. There is no ownership check to verify that auth.uid() equals the user_id column, so User A can access User B's data. Global access means all logged-in users get access to all data, so an internal threat actor can exfiltrate everything. There is missing tenant isolation with no organization or tenant checks, so cross-tenant data access is possible in SaaS applications.

A secure policy with tenant isolation verifies that the authenticated user owns the record and belongs to the correct organization. The policy checks that auth.uid() equals the user_id column and that the organization_id matches the org_id claim in the JWT.

ARSENAL ARCHITECTURE
--------------------

The arsenal is organized to follow the Supabase attack surface systematically with each module addressing a specific layer.

The supabase_arsenal.py file serves as the master orchestrator that runs everything. It contains the module execution engine, dependency management, result aggregation, and report coordination.

The reconnaissance directory handles the discovery phase and asks what exists. The project_mapper.py file performs auto-discovery of tables, functions, and buckets through OpenAPI specification parsing, table enumeration, RPC function discovery, storage bucket listing, and schema inference.

The auth directory handles the identity and authentication layer and asks who can access. The auth_audit.py file tests OAuth providers, verification requirements, and MFA configuration through provider enumeration, redirect validation, email verification testing, MFA configuration checking, and session security analysis.

The database directory handles the PostgreSQL layer and asks what they can access. The rls_audit.py file performs Row Level Security testing with anonymous read tests, anonymous write tests, authenticated read tests, ownership enforcement tests, and cross-tenant access tests. The schema_enum.py file performs complete schema enumeration with table listing, column identification, data type detection, sensitive column pattern matching, and relationship mapping. The function_audit.py file performs RPC function security analysis with function discovery, parameter injection testing, privilege context analysis, data return analysis, and sensitive function identification.

The storage directory handles the object storage layer and asks what files are exposed. The bucket_audit.py file tests bucket permissions, object listing, public access, file upload and download capabilities, and file deletion permissions.

The realtime directory handles the WebSocket layer and asks what channels are exposed. The channel_audit.py file tests channel subscription permissions, authentication requirements, and broadcast capabilities.

The secrets directory handles key exposure scanning and asks what credentials are exposed. The key_exposure.py file performs frontend JavaScript scanning for exposed keys and JWT tokens.

The report directory handles output generation and asks what the findings are. The findings.py file creates a unified HTML report with severity breakdown and remediation guidance.

MODULE DEEP-DIVE
----------------

Reconnaissance - Project Mapper

Purpose: Discover the entire attack surface without prior knowledge.

Why it exists: Attackers need to know what tables exist before testing them. This module leverages the auto-generated OpenAPI specification to discover all exposed database objects.

What it tests includes exposed tables and views, RPC functions, storage buckets, and schema structure including column names and data types.

Attack surface identified includes tables that should not be public, functions that expose internal logic, and buckets with listing permissions.

Technical implementation details include parsing the OpenAPI specification at the rest/v1 endpoint, extracting all paths that represent database objects, identifying RPC functions under the rpc path, listing storage buckets through the storage API, probing table schemas by requesting rows with a limit of zero, and analyzing content-range headers for access verification.

Required parameters include the Supabase project URL which defines the attack target, and the public anon key which provides the API access level being tested. Together these define what resources are accessible to an untrusted client.

Output is recon_results.json containing a full list of discovered objects with their access levels.

Usage command: python3 reconnaissance/project_mapper.py -u project_url -k anon_key

Auth - Authentication Auditor

Purpose: Test authentication configuration and provider security.

Why it exists: Authentication is the first trust boundary. Misconfigurations here can lead to account takeover, unauthorized access, or information disclosure.

What it tests includes email verification requirements, OAuth provider configurations, redirect URL validation for open redirect vulnerabilities, MFA availability, and session configuration.

Attack vectors tested include sign-up without email confirmation allowing disposable email abuse, OAuth redirect manipulation enabling credential theft, provider enumeration revealing supported third-party services, and session fixation possibilities.

Technical implementation details include attempting sign-up without verification to test the confirmation requirement, checking MFA endpoints for existence and accessibility, testing OAuth redirect URLs for validation weakness, enumerating providers by attempting authorization flows, analyzing session settings for expiration and refresh policies, and verifying token revocation mechanisms.

Required parameters include the Supabase project URL and the anon key for API access.

Output is auth_findings.json containing authentication weaknesses identified with severity ratings.

Usage command: python3 auth/auth_audit.py -u project_url -k anon_key

Database - RLS Auditor

Purpose: Test Row Level Security policies on every exposed table.

Why it exists: RLS is the primary security boundary in Supabase. The entire data protection model relies on properly configured policies. This is the most critical module.

What it tests includes anonymous read access to determine if the anon role can SELECT from tables, anonymous write access to determine if the anon role can perform INSERT, UPDATE, or DELETE operations, authenticated access to determine what authenticated users can access, and ownership enforcement to determine if users can access data belonging to others.

Understanding the tests is critical. The SELECT test with the anon key checks if anyone can read the table. If yes, sensitive data is exposed. The INSERT test with the anon key checks if anyone can insert into the table. If yes, data injection is possible. The SELECT test with an authentication token checks what authenticated users can read and may reveal horizontal privilege escalation. Ownership testing determines if User A can read User B's data and identifies IDOR vulnerabilities.

Technical implementation details include sending SELECT requests with limit one to minimize data extraction, attempting INSERT with minimal payloads to test write permissions, checking HTTP status codes and response bodies for access indicators, testing with both anon and authenticated JWTs for comparison, analyzing policy bypass attempts through parameter manipulation, and performing cross-user access tests when multiple tokens are available.

Required parameters include the Supabase project URL, the anon key for basic testing, and optionally an authenticated JWT token for testing logged-in user privileges.

What the JWT token provides includes the ability to test policies that require auth.uid() equal to user_id, revealing if authenticated users can access other users' data, and testing if administrators can be impersonated through role claims.

Output is rls_audit_results.json containing the complete RLS audit with severity ratings for each finding.

Usage command: python3 database/rls_audit.py -u project_url -k anon_key and optionally -a auth_jwt_token for authenticated testing

Database - Schema Enumerator

Purpose: Enumerate complete database schema including columns, relationships, and sensitive data patterns.

Why it exists: Understanding schema structure reveals sensitive columns, potential injection points, and data relationships that inform further attacks.

What it enumerates includes all tables in the public schema, column names and data types, primary and foreign key relationships, and sensitive columns containing patterns such as password, token, api_key, secret, email, phone, address, ssn, credit_card, passwd, pwd, auth_token, refresh_token, jwt, oauth, private, role, and admin.

Technical implementation details include querying the OpenAPI specification for table definitions, probing each table with a select star query limited to one row to retrieve column names, analyzing response headers for content-range information, detecting sensitive columns through pattern matching on column names, parsing data types from response payloads, and building a complete schema map.

The service_role flag indicates that the key being used is a service_role key which bypasses all RLS policies. This key is intended for backend servers only and finding it exposed is critical and indicates complete database compromise.

Required parameters include the Supabase project URL and the key being used, with the optional service_role flag.

Output is schema_enumeration.json containing the full schema with columns, data types, and sample data.

Usage command: python3 database/schema_enum.py -u project_url -k key and optionally --service-role for service_role key testing

Database - Function Auditor

Purpose: Audit RPC functions for privilege escalation, injection, and data exposure.

Why it exists: PostgreSQL functions executed through the rpc endpoint can run arbitrary database logic. Functions declared with SECURITY DEFINER run with elevated privileges and can be exploited.

What it tests includes function accessibility with empty parameters to determine if public execution is allowed, function behavior with various parameter inputs to identify injection points, sensitive function identification through naming patterns such as admin, config, system, exec, command, password, reset, privilege, grant, delete, drop, truncate, backup, export, import, and migrate, and data return analysis to determine what the function exposes.

Common attack patterns include privilege escalation where a function runs with higher privileges than the user and allows unauthorized operations, information disclosure where a function returns sensitive data such as other users' records, parameter injection where a function accepts unsafe parameters that can be manipulated, and function chaining where one function can be called to enable another and create a privilege escalation chain.

Technical implementation details include discovering functions through OpenAPI parsing, sending POST requests to the rpc endpoint with various parameter payloads, testing empty objects to probe for default behavior, attempting common parameter names such as id, limit, user_id, and email, analyzing response data for sensitive information, checking status codes for access indications, and identifying functions with SECURITY DEFINER behavior through response analysis.

Required parameters include the Supabase project URL and the anon key.

Output is function_audit.json containing accessible functions, their parameter requirements, and response data.

Usage command: python3 database/function_audit.py -u project_url -k anon_key

Storage - Bucket Auditor

Purpose: Test storage bucket security and object permissions.

Why it exists: Storage is often overlooked in security assessments. Public buckets can expose sensitive files, documents, backups, configuration files, and even executable code.

What it tests includes bucket listing permissions to determine if an attacker can enumerate buckets, object read permissions to determine if files can be downloaded, object upload permissions to determine if files can be injected, object delete permissions to determine if files can be removed, public versus private bucket status to identify exposure, and file overwrite permissions to determine if existing files can be replaced.

Attack vectors include data exposure where public buckets contain sensitive files such as documents, backups, and configuration files, malicious upload where arbitrary files can be uploaded for phishing, malware distribution, or code execution, file overwrite where existing files can be replaced for defacement or backdoor installation, and mass enumeration where all objects in a bucket can be listed.

Technical implementation details include sending GET requests to the bucket list endpoint, attempting to list objects in each discovered bucket, testing file uploads with test content to verify write permissions, attempting to download uploaded files to verify public accessibility, testing DELETE operations to verify removal permissions, checking bucket public status flags, and analyzing policy configurations.

Required parameters include the Supabase project URL and the anon key.

Output is storage_audit.json containing bucket access findings with severity ratings.

Usage command: python3 storage/bucket_audit.py -u project_url -k anon_key

Realtime - Channel Auditor

Purpose: Test realtime WebSocket channel security.

Why it exists: Realtime subscriptions can leak sensitive data if channels are misconfigured. Unauthorized users might subscribe to private channels and receive sensitive updates.

What it tests includes realtime service availability to determine if WebSocket upgrades are accepted, public channel access to determine if unauthenticated users can subscribe, authentication requirements to determine if keys or tokens are required, and channel subscription permissions to determine if access controls are enforced.

Technical implementation details include attempting WebSocket upgrade connections, sending HTTP requests to channel endpoints, testing common channel names such as public, realtime, events, notifications, messages, updates, all, broadcast, and wildcard patterns, analyzing response codes for 200, 401, 403, and 404 statuses, and testing both authenticated and unauthenticated access.

Required parameters include the Supabase project URL and the anon key.

Output is realtime_audit.json containing channel security findings.

Usage command: python3 realtime/channel_audit.py -u project_url -k anon_key

Secrets - Key Exposure Scanner

Purpose: Scan frontend code for exposed Supabase keys.

Why it exists: The service_role key or JWT secret should never appear in frontend code. This module crawls target applications to find exposed credentials.

What it scans for includes anon keys which are expected but part of the attack chain, service_role keys which are critical and indicate immediate compromise, JWT secrets which are critical and enable token forging, environment variables containing configuration, and configuration in JavaScript bundles.

Technical implementation details include crawling the target application's base URL, downloading HTML pages and analyzing content, extracting JavaScript file references from script tags, downloading and parsing JavaScript bundles, scanning for regular expression patterns matching JWT tokens and Supabase configuration strings, identifying environment variable patterns such as NEXT_PUBLIC_SUPABASE_URL, REACT_APP_SUPABASE_ANON_KEY, and VITE_SUPABASE_KEY, and analyzing string literals for credential patterns.

Required parameters include the target application URL to crawl, which is not the Supabase URL.

Output is key_exposure.json containing found keys with severity ratings.

Usage command: python3 secrets/key_exposure.py -u target_application_url

Report - Findings Aggregator

Purpose: Aggregate all audit results into a comprehensive report.

Why it exists: Documentation is critical for professional assessments. This module creates a professional report that can be shared with stakeholders, clients, or used for remediation tracking.

Technical implementation details include loading all JSON result files from the audit modules, parsing findings by severity and module, calculating severity statistics, generating an HTML report with findings organized by severity, including evidence snippets for verification, providing remediation recommendations based on finding types, and creating a printable format for sharing.

Required parameters include the optional output file name.

Output is supabase_report.html containing the complete audit report with severity breakdown.

Usage command: python3 report/findings.py and optionally -o report_name.html

Orchestrator - Supabase Arsenal

Purpose: Master orchestrator that runs all modules and generates a unified report.

Why it exists: Efficiency is critical. Running a complete assessment should be a single command. This orchestrator manages dependencies, sequences modules appropriately, and handles errors gracefully.

Technical implementation details include dependency management to ensure modules run in correct order, result aggregation to collect outputs from all modules, error handling to continue assessments even when individual modules fail, progress reporting to show assessment status, and report coordination to generate the final output.

Required parameters include the Supabase project URL and the anon key, with an optional authenticated JWT for authenticated testing.

Output is the complete assessment with all JSON result files and the final HTML report.

Usage command: python3 supabase_arsenal.py -u project_url -k anon_key and optionally -a auth_jwt_token

COMPLETE ASSESSMENT WORKFLOW
----------------------------

Phase 1 - Reconnaissance

Run the project mapper to discover all exposed tables, functions, and buckets.

python3 reconnaissance/project_mapper.py -u project_url -k anon_key

This identifies the complete attack surface before deeper testing.

Phase 2 - Key Exposure External

Scan the target application for exposed keys and JWT tokens.

python3 secrets/key_exposure.py -u target_application_url

This identifies if service_role keys or JWT secrets are exposed in frontend code.

Phase 3 - Authentication Audit

Test authentication configuration, providers, and verification requirements.

python3 auth/auth_audit.py -u project_url -k anon_key

This reveals weaknesses in the authentication layer.

Phase 4 - Database Security

The most critical phase. Run schema enumeration to understand the database structure.

python3 database/schema_enum.py -u project_url -k anon_key

Run RLS audit to identify missing or weak policies.

python3 database/rls_audit.py -u project_url -k anon_key

Run RLS audit with authenticated JWT for ownership testing.

python3 database/rls_audit.py -u project_url -k anon_key -a auth_jwt

Run function audit to identify privileged RPC functions.

python3 database/function_audit.py -u project_url -k anon_key

Phase 5 - Storage Security

Test bucket permissions and object access.

python3 storage/bucket_audit.py -u project_url -k anon_key

Phase 6 - Realtime Security

Test WebSocket channel security.

python3 realtime/channel_audit.py -u project_url -k anon_key

Phase 7 - Reporting

Generate the unified HTML report.

python3 report/findings.py -o supabase_assessment_report.html

Phase 8 - Full Orchestration

Run everything with a single command.

python3 supabase_arsenal.py -u project_url -k anon_key -a auth_jwt

FINDING SEVERITY MATRIX
-----------------------

Critical Severity indicates immediate compromise risk. Examples include service_role key exposure where the service role key is found in frontend code allowing complete database takeover, RLS disabled on sensitive tables such as users or payments tables allowing full data extraction, and JWT secret exposure allowing token forgery and impersonation of any user.

High Severity indicates significant data breach potential. Examples include public bucket with sensitive files containing documents, backups, or credentials, weak RLS policies allowing authenticated users to access all data without ownership checks, authenticated users accessing other users' data through IDOR, and public exposure of administrative functions.

Medium Severity indicates information disclosure. Examples include schema enumeration revealing internal database structure, provider enumeration revealing supported OAuth providers, email verification bypass allowing disposable email accounts, and bucket listing exposing file names without content.

Low Severity indicates minimal risk. Examples include missing security headers such as CORS or CSP, verbose error messages revealing internal paths, and outdated library versions without known exploits.

Info Severity indicates informational findings. Examples include enabled OAuth providers showing the authentication landscape, discovered endpoints for internal reference, and schema structure for documentation purposes.

UNDERSTANDING THE ANON KEY IMPLICATIONS
---------------------------------------

If the anon key allows reading any table, the severity is Critical and the implication is complete data exposure.

If the anon key allows writing to any table, the severity is High and the implication is data corruption or injection.

If the anon key allows executing sensitive functions, the severity is High and the implication is privilege escalation.

If the anon key allows accessing storage, the severity is Medium and the implication is file exposure or upload.

If the anon key allows listing buckets, the severity is Low and the implication is information disclosure.

TESTING METHODOLOGY REFERENCE
-----------------------------

Row Level Security Testing Approach

The core testing approach for RLS involves sending authenticated and unauthenticated requests to each discovered table and analyzing the response.

For anonymous read testing, send a GET request to the rest endpoint for the table with a select star query limited to one. If the response status is 200 and data is returned, RLS is missing or misconfigured. If the response is 200 with empty brackets, the table exists but has no accessible data. If the response is 403, RLS is properly blocking access.

For anonymous write testing, send a POST request to the rest endpoint for the table with a minimal payload. If the response status is 201, inserts are allowed without authentication. If the response is 403, writes are blocked.

For authenticated access testing, repeat the above tests using a valid JWT token. If authenticated users can read all data regardless of ownership, there is a policy weakness. If authenticated users can access only their own data through proper ownership checks, RLS is correctly implemented.

For cross-tenant access testing, attempt to access records from different organizations using the JWT token. If the organization_id claim is not enforced in policies, cross-tenant access is possible.

Schema Enumeration Approach

The schema enumeration process involves discovering all tables and their columns through the OpenAPI specification and through direct probing.

The OpenAPI specification at the rest root endpoint provides the complete schema definition when accessible. This reveals all tables, views, and functions with their input and output schemas.

Direct probing involves sending a select star query with limit one to each discovered table. The response reveals column names and data types through the JSON structure. The Content-Range header in the response reveals pagination information and confirms table existence.

Sensitive column detection involves pattern matching on column names for known sensitive patterns. Common patterns include password, passwd, pwd, token, secret, key, api_key, auth_token, refresh_token, jwt, oauth, private, role, admin, email, phone, address, ssn, credit_card.

Function Audit Approach

The function audit involves discovering RPC functions through the OpenAPI specification and testing their accessibility and behavior.

Function discovery involves parsing the OpenAPI specification for paths under rpc. Each discovered function represents a potential attack vector.

Accessibility testing involves sending POST requests to the rpc endpoint for each function with an empty JSON object. If the response is 200, the function is accessible with default parameters. If the response is 400, parameters are required. If the response is 403, the function is protected.

Parameter testing involves attempting common parameter names such as id, limit, user_id, email, and others. Successfully accessing functions with these parameters reveals function behavior and potential injection points.

Sensitive function detection involves pattern matching on function names for admin, config, system, exec, command, password, reset, privilege, grant, delete, drop, truncate, backup, export, import, and migrate patterns.

Storage Audit Approach

The storage audit involves listing buckets, testing object permissions, and analyzing public access.

Bucket listing involves sending a GET request to the storage bucket endpoint. If the response is 200 with a list of buckets, the anon key has listing permissions.

Object listing involves sending a GET request to the object list endpoint for each bucket. If the response is 200 with a list of objects, the bucket allows enumeration.

File upload testing involves sending a POST request with test content to each bucket. If the response is 200 or 201, uploads are allowed.

File download testing involves sending a GET request to the public object endpoint for uploaded files. If the response is 200, uploaded files are publicly accessible.

File deletion testing involves sending a DELETE request to the object endpoint. If the response is 200, deletions are allowed.

Realtime Audit Approach

The realtime audit involves testing WebSocket accessibility and channel subscription permissions.

Service availability testing involves attempting a WebSocket upgrade connection to the realtime endpoint. If the upgrade succeeds, the service is available.

Channel access testing involves sending HTTP requests to channel endpoints with common channel names. If the response is 200, the channel is accessible without authentication. If the response is 403, authentication is required.

Authentication requirement testing involves attempting WebSocket connections without authentication headers. If the connection is accepted, authentication is not enforced.

OUTPUT FILES REFERENCE
----------------------

The Project Mapper outputs recon_results.json containing discovered tables, functions, and buckets.

The Auth Auditor outputs auth_findings.json containing authentication configuration issues.

The RLS Auditor outputs rls_audit_results.json containing RLS policy violations by table.

The Schema Enumerator outputs schema_enumeration.json containing complete table schemas with columns and data types.

The Function Auditor outputs function_audit.json containing accessible RPC functions and their responses.

The Storage Auditor outputs storage_audit.json containing bucket permissions and access findings.

The Realtime Auditor outputs realtime_audit.json containing channel security issues.

The Key Exposure Scanner outputs key_exposure.json containing exposed keys and tokens.

The Report Generator outputs supabase_report.html containing the unified HTML report.

ENVIRONMENT SETUP
-----------------

Dependencies required include requests for HTTP operations, python-dateutil for timestamp handling, and json for data serialization and parsing.

Installation command: pip install requests python-dateutil

Directory structure required includes reconnaissance, auth, database, storage, realtime, secrets, and report directories.

Permissions required include execute permissions on all Python scripts.

Setup commands include mkdir -p reconnaissance auth database storage realtime secrets report and chmod +x supabase_arsenal.py and chmod +x each module.

QUICK START GUIDE
-----------------

Navigate to the Supabase arsenal directory: cd ~/Desktop/jericho/baas/supabase

Run the full assessment: python3 supabase_arsenal.py -u project_url -k anon_key -a auth_jwt

Review the report by opening supabase_report.html in a browser.

For individual modules, refer to the specific usage commands in each section above.

IMPORTANT NOTES
---------------

Authorization Required: Only use these tools on targets you own or have explicit permission to test. Unauthorized access is illegal.

Rate Limiting: Supabase has rate limits. Use responsibly to avoid triggering protection mechanisms and account suspension.

JWT Tokens: If you obtain an authenticated JWT, use it for testing. It reveals what authenticated users can access that anonymous users cannot.

Service Role Key: Finding a service_role key is a critical finding. It allows full database access bypassing all RLS policies.

Report Customization: The HTML report can be customized by modifying the template in report/findings.py.

NEXT STEPS AFTER ASSESSMENT
---------------------------

Prioritize findings by addressing Critical and High findings immediately.

Implement RLS by enabling RLS on all tables and creating proper policies with ownership enforcement.

Review Auth by ensuring MFA, email verification, and proper OAuth configuration are implemented.

Secure Storage by making buckets private by default and implementing proper access policies.

Rotate Keys by regenerating the service_role key if it was exposed.

Audit Functions by reviewing all RPC functions for SECURITY DEFINER misuse and parameter validation.

Test Remediation by rerunning the assessment after fixes are applied.

Document Findings by maintaining a security posture document for ongoing monitoring.

REFERENCES
----------

Supabase Documentation at supabase.com provides the official API reference and security guidelines.

PostgREST Documentation at postgrest.org provides REST API implementation details.

PostgreSQL Row Level Security documentation provides the underlying security model.

OWASP API Security Top 10 provides industry standards for API security testing.

Jericho - And the walls came tumbling down.
