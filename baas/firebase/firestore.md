# Cloud Firestore Assessment & Exploitation

Cloud Firestore is a flexible, scalable NoSQL document database. Since clients query Firestore directly via Google's client SDKs, security relies entirely on **Firestore Security Rules**. When rules are poorly designed, attackers can bypass access controls to read, modify, or delete sensitive collections.

---

## 1. Understanding Firestore Security Rules

Firestore rules use a declarative match-and-allow structure:

```javascript
service cloud.firestore {
  match /databases/{database}/documents {
    match /<collection>/{document} {
      allow read, write: if <condition>;
    }
  }
}
Common Rule Misconfigurations
A. The Global Open Trap
Often used during development and forgotten. Anyone can read or write any document.

JavaScript
match /{document=**} {
  allow read, write: if true;
}
B. The "Authenticated-Only" Fallacy
Developers often assume that requiring authentication is enough. However, this allows any registered Firebase user (including an attacker who self-registers) to read or write other users' data.

JavaScript
match /users/{userId} {
  allow read, write: if request.auth != null;
}
C. Write-Only but No Read Protections
Sometimes developers secure writes but allow public reads, exposing internal application configurations, PII, or access logs.

JavaScript
match /logs/{logId} {
  allow read: if true;
  allow write: if request.auth.token.admin == true;
}
2. Enumerating Firestore via API Endpoints
Firestore exposes its data through a REST API. If rules are permissive, you can query endpoints directly without using the Firebase SDK.

Checking for Public Collection Dumps
To test if a specific collection is readable, send a request to the structured Firestore REST endpoint:

Bash
curl -s -X GET "[https://firestore.googleapis.com/v1/projects/](https://firestore.googleapis.com/v1/projects/)<PROJECT_ID>/databases/(default)/documents/<COLLECTION_NAME>"
Vulnerable (200 OK): Returns a JSON payload containing the structured documents within that collection.

Secured (403 Forbidden): Returns a permission denied error.

Automating the Audit
You can run automated scanning to find exposed collections using simple bash loops:

Bash
for col in users configurations settings profiles orders transactions; do
  echo "[*] Testing collection: $col"
  curl -s -o /dev/null -w "%{http_code}" "[https://firestore.googleapis.com/v1/projects/](https://firestore.googleapis.com/v1/projects/)<PROJECT_ID>/databases/(default)/documents/$col"
  echo ""
done
3. Remediating Firestore Rules
To secure your Firestore instance, rules must enforce strict resource ownership and validate inputs.

Secure User-Owned Rules
The auth.uid must match the specific document ID of the user record being accessed:

JavaScript
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
