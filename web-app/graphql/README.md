# GraphQL Enumeration

Read-only helpers for checking unauthenticated or explicitly low-privilege GraphQL exposure.

## Tools

* `endpoint_probe.py`: Checks common GraphQL paths with a minimal `__typename` query.
* `introspection_probe.py`: Attempts standard introspection and saves the schema JSON when exposed.

## Examples

```bash
python endpoint_probe.py -b https://target.example
python introspection_probe.py -u https://target.example/graphql
python introspection_probe.py -u https://target.example/graphql -H "Authorization: Bearer <low_priv_token>"
```

No brute force, mutation, or bypass logic is included. Use only on authorized targets.
