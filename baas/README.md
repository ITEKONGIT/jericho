# BaaS Security Module

This module provides an offensive framework for auditing Backend-as-a-Service (BaaS) architectures, focusing on misconfigurations in Supabase and Firebase.

## Newcomer ramp

**What this field is.** BaaS means the backend is someone else's managed product — Supabase, Firebase — configured through a web console and reachable directly from the browser. The rules that would normally live in server code ("this user can read this row") live in *config*: Row Level Security policies, security rules, key scoping. The frontend talks to the database almost directly.

**Why people miss findings here.** Two reasons. First, the config *looks* like code, so it gets audited like code — but a policy that says `auth.uid() = user_id` still depends on whether signup is open and what a user can write to their own metadata. Second, the deepest bug in this module isn't in the config at all: a `service_role` key in the frontend bundle bypasses RLS *by design*, so the airtight policy is irrelevant. The recurring miss: **auditing the rules without auditing what can bypass them.**

**Read order.** Pipeline first (below): introspection → policy probing → identity analysis → admin takeover. Then the arsenal in pipeline order — [`reconnaissance/`](supabase/reconnaissance/), [`database/`](supabase/database/), [`auth/`](supabase/auth/), [`storage/`](supabase/storage/), [`realtime/`](supabase/realtime/), [`secrets/`](supabase/secrets/), [`report/`](supabase/report/). Firebase notes ([`firebase/`](firebase/)) parallel the same questions with different config surfaces. **Defer:** `function_audit.py` and realtime channels until the target actually uses functions/realtime — they're later steps in the same pipeline, not new theory.

## Supabase Arsenal
The `supabase/` directory contains an orchestration suite for:
- **Project Discovery**: Mapping schema, RPC functions, and storage buckets.
- **RLS Audit**: Probing Row-Level Security policies for unauthorized data access (READ/WRITE).
- **Authentication Assessment**: Testing OAuth configurations and JWT verification flows.
- **Signup-to-Admin Review**: Identifying cases where open signup plus weak RLS or route guards exposes admin dashboards.
- **Secret Exposure**: Harvesting `anon` and `service_role` keys from frontend environments.

## Assessment Pipeline
1. **Introspection**: Dumping the OpenAPI specification via the PostgREST endpoint.
2. **Policy Probing**: Testing anonymity against table-level permissions.
3. **Identity Analysis**: Verifying ownership enforcement via authenticated JWTs.
4. **Administrative Takeover**: Identification of `service_role` key exposure.

---
*Jericho: Serverless infrastructure auditing.*
