# Methodology: Frontend Encryption Analysis (Deep Dive)

## 1. Engineering Nuances
Developers often implement frontend encryption to combat "Man-in-the-Middle" (MitM) or to prevent data leakage in logging systems. However, the engineering reality is that **the client is an untrusted environment**. 

### The Key Derivation Nuance (KDF)
Developers rarely use a raw key. They implement Key Derivation Functions (KDFs). If you see `PBKDF2` or `Argon2` in the JS bundle, the "Key" isn't a string; it's a result of:
* **The Salt:** Often hardcoded or fetched from a non-secure API endpoint.
* **The Iteration Count:** If this is too low, the entropy is compromised.
* **The Secret:** Often a static string (e.g., `process.env.APP_SECRET` during build time).

## 2. The Implementation Lifecycle (The Developer's Flow)
To effectively bypass this, you must understand the sequence:
1. **The Binding Event:** Identify the event listener (e.g., `form.submit`) that triggers the `encrypt()` function. 
2. **The Buffer Transformation:** Before `AES-GCM` or `RSA` encryption, developers often perform a `JSON.stringify()` or `btoa()` (Base64) on the payload. **Note:** If you find the encryption function, look for what it receives *before* the transform.
3. **The Transmission Protocol:** Developers often implement a custom wrapper, meaning the data isn't just encrypted; it's also *packaged* in a custom format (e.g., `{"v": 1, "ct": "encrypted_blob", "iv": "..."}`).

## 3. Advanced Bypass Techniques
* **Monkey Patching the Crypto Engine:** Instead of reversing the whole logic, hook the crypto library in the browser console.
  ```javascript
  // Example: Hooking AES-GCM
  const originalEncrypt = window.crypto.subtle.encrypt;
  window.crypto.subtle.encrypt = function(algo, key, data) {
      console.log("Captured Plaintext:", new TextDecoder().decode(data));
      return originalEncrypt.apply(this, arguments);
  };
Dependency Analysis: Search for package.json in the leaked .git directory. If they use crypto-js, look up the exact version. Older versions have documented vulnerabilities (e.g., poor padding) that allow for "padding oracle" style attacks against the frontend.

4. Why "Novel" Encryption Fails
The engineering flaw is almost always the lack of server-side secret validation. Developers assume that because the data arrived encrypted, the client must have used the correct key. Often, the server simply decrypts whatever the client sends, trusting the client's self-generated IV (Initialization Vector). This is the golden path for manipulation.

Jericho Framework: Mapping the developer's logic to your exploit.
