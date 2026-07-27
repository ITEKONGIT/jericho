# Supabase Signup To Admin Dashboard Exposure

This finding chain happens when Supabase Auth is open enough to let a new user register, while the application trusts weak role checks, frontend route guards, or incomplete RLS policies. The result is that a normal self-registered account can reach admin data or admin UI paths.

## Common Chain

1. Public frontend exposes the Supabase URL and anon key.
2. Signup is enabled through Supabase Auth.
3. Email confirmation, invite-only controls, domain allowlists, or approval flows are missing.
4. The new account receives an authenticated JWT.
5. The app treats `authenticated` as enough privilege for sensitive reads or admin routes.
6. RLS policies check only `auth.role() = 'authenticated'` instead of ownership, tenant, or role.
7. Admin dashboard APIs return data because backend authorization is weaker than the UI guard.

## What To Check

During an authorized assessment, create a low-privilege test account through the normal signup flow and compare it against expected access.

Check the signup posture:

* Is public signup enabled?
* Is email confirmation required before data access?
* Are disposable or arbitrary domains allowed?
* Is the app meant to be invite-only, but Supabase Auth accepts public signup?
* Does signup automatically create a profile, organization, role, or team membership?
* Can user-controlled metadata influence role, plan, tenant, or admin flags?

Check dashboard access:

* Can the new account load admin frontend routes directly?
* Do admin routes rely only on frontend route guards?
* Do admin API calls work if copied from a privileged browser session and replayed with the new account token?
* Do tables return data to any authenticated user?
* Do RPC functions expose admin data to authenticated users?
* Do storage buckets or realtime channels expose admin-only material?

## RLS Red Flags

Weak policy examples:

```sql
using (auth.role() = 'authenticated')
```

```sql
using (true)
```

```sql
using (auth.uid() is not null)
```

These policies prove login, not authorization. They do not prove ownership, tenant membership, or admin status.

Safer policy shape:

```sql
using (
  auth.uid() = user_id
  or exists (
    select 1
    from memberships
    where memberships.user_id = auth.uid()
      and memberships.org_id = target_table.org_id
      and memberships.role in ('owner', 'admin')
  )
)
```

The exact policy depends on the schema, but the important property is that it validates the authenticated user against the protected object.

## Admin Role Mistakes

Supabase projects often store role state in one of three places:

* JWT app metadata.
* A `profiles`, `users`, or `memberships` table.
* Frontend state loaded after login.

High-risk mistakes:

* Trusting `user_metadata` for roles. Users may be able to influence it depending on the flow.
* Using frontend-only role checks.
* Letting signup insert a default role that admin endpoints accept.
* Failing to separate internal admins from normal authenticated users.
* Not validating tenant membership before returning dashboard data.

Developer fix:

* Store authoritative roles server-side or in trusted `app_metadata`.
* Never trust user-editable metadata for authorization.
* Re-check role and tenant membership in RLS policies and backend functions.
* Make admin APIs fail closed without a verified admin role.

## Developer Fix Checklist

* Disable public signup when the product is invite-only.
* Require email confirmation before granting meaningful access.
* Enforce domain allowlists where appropriate.
* Create users with the lowest possible default privilege.
* Enable RLS on every non-public table.
* Replace broad `authenticated` policies with ownership and tenant-aware policies.
* Audit RPC functions for `SECURITY DEFINER` and admin-only logic.
* Keep admin dashboards behind server-side authorization, not frontend route checks.
* Test with a freshly signed-up user and expect admin routes, data, buckets, channels, and functions to fail.

Use only on systems where you have authorization to test.
