# Firebase Security Assessment & Hardening

This directory contains methodologies, automated scripts, and structural exploitation rules for auditing Firebase deployments. 

Firebase shifts the burden of access control entirely to the client-side via JSON rules and configuration files. This makes it highly prone to developer oversights.

## Attack Surface Areas

### 1. Realtime Database (`realtime-db.md`)
* Default unauthenticated open reads/writes (`.json` endpoints).
* Data injection and system takeover through permissive structural rules.

### 2. Cloud Firestore (`firestore.md`)
* Insecure rules evaluating authentication status (`request.auth != null`) without verifying resource ownership.
* NoSQL schema mapping and extraction.

### 3. Anonymous Auth Exploitation
* Generating valid application JSON Web Tokens (JWTs) via anonymous sign-up endpoints to bypass authentication-only checks.
