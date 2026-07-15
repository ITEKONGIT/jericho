# BaaS Security Module

This module provides an offensive framework for auditing Backend-as-a-Service (BaaS) architectures, focusing on misconfigurations in Supabase and Firebase.

## Supabase Arsenal
The `supabase/` directory contains an orchestration suite for:
- **Project Discovery**: Mapping schema, RPC functions, and storage buckets.
- **RLS Audit**: Probing Row-Level Security policies for unauthorized data access (READ/WRITE).
- **Authentication Assessment**: Testing OAuth configurations and JWT verification flows.
- **Secret Exposure**: Harvesting `anon` and `service_role` keys from frontend environments.

## Assessment Pipeline
1. **Introspection**: Dumping the OpenAPI specification via the PostgREST endpoint.
2. **Policy Probing**: Testing anonymity against table-level permissions.
3. **Identity Analysis**: Verifying ownership enforcement via authenticated JWTs.
4. **Administrative Takeover**: Identification of `service_role` key exposure.

---
*Jericho: Serverless infrastructure auditing.*
