# Classes People Miss

The named vulnerability types — SQLi, XSS, buffer overflow, IDOR — get taught everywhere. This file is the other shelf: classes that don't show up as named types in a textbook, because they look like *valid* evidence right up until they're not.

**The common thread:** almost everything in this list hides behind something that *checks out*. A signature that verifies. A scanner that returns clean. A cipher that's strong. An address that resolves. The miss is never "I didn't know that bug existed" — it's "the signal I trusted told me there was nothing here."

Each entry says why the class gets missed, and links to where this repo covers it. When I hit a target and feel like there's nothing to find, I read this list instead of repeating the scans.

---

## Web & identity

### Token confusion — the token is cryptographically valid, for the wrong thing
The signature verifies, so the check passes. But the backend only ever checked the signature — not the audience, issuer, tenant, or token *purpose*. An `id_token` works as an `access_token`. A password-reset token works as a session. A staging-tenant token works in production.
**Why it's missed:** testers replay the *correct* token class and conclude auth works. The confusion only appears when you deliberately present the wrong token and watch it get accepted anyway.
**First question:** does any endpoint reject a validly-signed token of the wrong type?
**Covered in:** [web-app/token-confusion/](../web-app/token-confusion/)

### Post-logout cache and token exposure — "logged out" is a client-side event
Logout clears the browser. The token still works until expiry, and authenticated responses may still be cached under a key that no longer means anything. Replay the captured request after logout — fresh data comes back.
**Why it's missed:** logout is tested by what the *screen* does, not by replaying traffic afterward. Nobody re-sends the post-logout request.
**First question:** after logging out, does the old token still return data?
**Covered in:** [web-app/cache-invalidation/](../web-app/cache-invalidation/)

### Auth endpoints that outlive their auth
Endpoints that work with auth headers, cookies, API keys, or JWT claims removed or tampered — because authorization was enforced by the *frontend* hiding the button, not the backend checking the request.
**Why it's missed:** the app never shows you the unauthenticated path, so you never click it. The check is what the UI allows, not what the server accepts.
**First question:** what happens if I just... don't send the auth header?
**Covered in:** [web-app/auth-endpoints/](../web-app/auth-endpoints/)

### Source maps shipped to production
`.map` files turn the minified bundle back into the original source: routes, API paths, auth logic, sometimes keys and encryption material. The frontend's entire design is readable.
**Why it's missed:** it's not a vulnerability on any page — it's a file that sits next to the pages. Nothing "fails" when you visit the site.
**First question:** does `/static/js/main.*.js.map` return 200?
**Covered in:** [web-app/source-maps/](../web-app/source-maps/)

### Frontend encryption breaks at key management, not the cipher
The crypto is real — AES-256, correct modes. It doesn't matter: the key was derived in JavaScript, in the browser, from material the browser already had. The trace starts at the bundle, not at the cipher name.
**Why it's missed:** people see strong crypto and stop. The failure is one step before the cipher — derivation, storage, or the developer's own encryption lifecycle.
**First question:** where did this key come from, and could I have watched it arrive?
**Covered in:** [docs/methodology/frontend-encryption.md](methodology/frontend-encryption.md)

## BaaS & cloud

### The `service_role` key in the frontend bundle
Supabase RLS can be airtight — and irrelevant, because the bundle ships a key that *bypasses* RLS by design. The database is well-configured; the secret is on the client.
**Why it's missed:** the audit targets the database config, which is genuinely good. The bug isn't in the database — it's in what got embedded in the frontend.
**First question:** which keys are in the JS bundle, and what does each one bypass?
**Covered in:** [baas/supabase/secrets/](../baas/supabase/secrets/)

### Open signup plus weak RLS equals admin dashboard
Auth works perfectly. Anyone can *sign up* — and the admin check is a client-side route guard or a nullable role column. Register, flip your own metadata, walk into the dashboard.
**Why it's missed:** signup isn't treated as an attack surface because "it's just registration." The takeover happens through the front door, with a legitimate account.
**First question:** what does a brand-new account see that it shouldn't?
**Covered in:** [baas/supabase/auth/](../baas/supabase/auth/)

### The management plane nobody remembers exists
`*.azurewebsites.net` is the app. `*.scm.azurewebsites.net` is Kudu — the deployment engine — and an exposed one is effectively an unauthenticated management console with RCE behind it. Same domain, one label people forget.
**Why it's missed:** the assessment targets the application URL. The management endpoint is a separate host that inherits the same credentials and is rarely in scope by accident.
**First question:** does the `-scm-` host exist, and does it accept these credentials?
**Covered in:** [exploits/kudu/](../exploits/kudu/)

### Metadata service SSRF on cloud hosts
A host inside a cloud network trusts its own metadata endpoint — and any SSRF on that host can fetch cloud credentials from it. Not a web bug; a placement bug.
**Why it's missed:** it needs a foothold *inside* the network first, and it looks like an infrastructure detail rather than an exploit path.
**First question:** from this box, can I reach `169.254.169.254`?
**Covered in:** [cloud-enum/Host-Audit/](../cloud-enum/Host-Audit/)

## Network & hardware

### Assets that don't answer the questions the scanner asks
WS-Discovery devices — printers, cameras, IoT — respond to UDP multicast, not ICMP or TCP sweeps. The scan comes back clean. The network is not clean.
**Why it's missed:** the scanner asks TCP/ICMP questions and takes silence as an answer. The devices were never listening on those terms.
**First question:** what's on the network that a TCP sweep structurally cannot see?
**Covered in:** [internal/discovery/](../internal/discovery/)

### Printers as first-class hosts
Port 9100 speaks raw. PJL/PCL/PostScript can expose memory, stored jobs, credentials, and filesystem access — the printer is a computer that nobody patched and everybody forgot.
**Why it's missed:** it's inventoried as a printer, not a host. It doesn't run anything "important," so nobody assigns it a threat model.
**Covered in:** [internal/printers/](../internal/printers/)

## Mobile

### "No traffic in the proxy" means the proxy was avoided, not that there's no traffic
Apps ignore system proxy settings or run custom networking stacks. The interception looks empty; the app is talking fine.
**Why it's missed:** the empty proxy is read as a result ("nothing interesting") instead of as a signal ("force the traffic through anyway" — iptables + ADB).
**First question:** is the app *refusing* to proxy, or is there genuinely nothing?
**Covered in:** [mobile/network/](../mobile/network/)

### Pinning that lives below the Java layer
The Frida hooks fire, the bypass loads, and the app still won't talk to the proxy — because the pinning is implemented natively, in C, where `TrustManagerImpl` hooks never reach.
**Why it's missed:** the standard bypass *appears to work* (no errors), so the failure reads as "the app is weird" instead of "wrong layer."
**First question:** which layer is actually doing the verification?
**Covered in:** [docs/methodology/mobile-reversing.md](methodology/mobile-reversing.md), [mobile/ssl-pinning/](../mobile/ssl-pinning/)

## Binary

### "GNU_STACK missing" is the opposite of what it looks like
A missing GNU_STACK header reads like an omission — nothing to worry about. It means the kernel falls back to a legacy default: an **executable** stack. The protection report that looks incomplete is actually the green light for ret2shellcode.
**Why it's missed:** absence is read as "no information" rather than as a default setting with offensive value.
**First question:** what does the *absence* of this field mean, not just its presence?
**Covered in:** [binary-exploitation/README.md](../binary-exploitation/README.md) (GNU_STACK), [binary-exploitation/notes/methodology.md](../binary-exploitation/notes/methodology.md)

### Format strings don't care about checksec
The one corruption class not blocked by a hardened protection profile. NX, canary, PIE, Full RELRO — none of it prevents the bug from existing; the protections only constrain where a format-string write can land.
**Why it's missed:** a strong checksec read-out ends the assessment early. The profile is treated as a verdict on the whole binary instead of a filter on specific shapes.
**First question:** does my input ever reach a printf-family call as the *format argument*?
**Covered in:** [binary-exploitation/shapes/format-string/](../binary-exploitation/shapes/format-string/)

### The function named exactly what you were looking for — and isn't
`grant_access` in `nm` looks like a win function. Disassemble it: it's the *gate check* that prints the failure message. A misnamed function that exits looks exactly like a broken exploit, and the shape gets abandoned.
**Why it's missed:** the symbol name is trusted as documentation. Names are written by the developer, not the compiler — verify by reading the code.
**First question:** what does this function actually *do*, before I aim anything at it?
**Covered in:** [binary-exploitation/shapes/ret2win/](../binary-exploitation/shapes/ret2win/)

---

## How to use this list

- **Before a test:** skim the "first question" column against the target type. Two minutes.
- **During a dead end:** the miss is usually that a signal was read as a result. Re-read the common thread.
- **When writing up findings:** if a finding here appeared, say *why it was missed* — that's the part that makes the report teach the next person.

---

*Jericho: And the walls came tumbling down. For authorized security assessments only.*
