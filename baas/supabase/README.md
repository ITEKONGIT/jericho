# Supabase Security Assessment & Hardening

This directory contains methodologies and exploitation techniques for auditing Supabase architectures. 

Unlike Firebase, Supabase is built on a traditional relational database (PostgreSQL). It automatically exposes the database schema via an auto-generated REST API (PostgREST) and GraphQL. Security relies heavily on PostgreSQL **Row Level Security (RLS)** policies.

## Attack Surface Areas

### 1. PostgREST API & RLS Misconfigurations (`postgrest-rls.md`)
* Bypassing permissive or entirely absent RLS policies.
* Exploiting `auth.role() = 'authenticated'` logic flaws.
* `service_role` key leakage and privilege escalation.

### 2. Storage & RPC Exploitation
* Identifying public buckets and missing storage access policies.
* Abusing exposed Remote Procedure Calls (RPC) for Server-Side Request Forgery (SSRF) or internal network mapping.
