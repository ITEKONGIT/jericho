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

## 3. JavaScript Trace Workflow
Start from the browser, not the cipher name. The most reliable path is to map every JavaScript file loaded by the page, then trace the main application and authentication logic until you find where sensitive payloads are assembled.

1. **Inventory Loaded Scripts:** Use DevTools Network/Sources to list all loaded JS bundles, sourcemaps, lazy chunks, and auth-related modules.
2. **Find Main/Auth Entrypoints:** Search for names like `main`, `app`, `auth`, `login`, `session`, `encrypt`, `decrypt`, `token`, `key`, `iv`, `nonce`, and `crypto`.
3. **Trace The Data Path:** Follow the value before encryption, through any encoding or KDF, into the final request body.
4. **Watch Runtime Storage:** Check `localStorage`, `sessionStorage`, IndexedDB, cookies, and in-memory globals for keys, salts, token-derived secrets, and encryption config.
5. **Set Breakpoints:** Break on `fetch`, `XMLHttpRequest.send`, `crypto.subtle.encrypt`, CryptoJS calls, and custom request wrappers.

## 4. Common Key Architectures

### Static Frontend Key
The encryption key or KDF secret is present in the client. This usually appears in two forms:

* **Backend-loaded storage key:** The app fetches a key or config object from the backend, then stores it in `localStorage` or `sessionStorage`.
* **Hardcoded bundle key:** The key, salt, or secret is embedded directly in the JavaScript bundle at build time.

Both are reversible because the browser must possess the material needed to encrypt the request.

### Split Static And Ephemeral Keys
Some apps combine a hardcoded frontend key with a backend-issued key that expires. The frontend may derive a final encryption key from both pieces, then renew the backend key when it expires so the server can still decrypt incoming payloads.

Assess this flow by identifying:

* The static frontend key or salt.
* The endpoint that issues the backend key.
* The expiry timestamp or lease duration.
* The renewal path.
* The derivation function that combines both key sources.
* Whether old backend keys are rejected server-side or only treated as expired client-side.

The weakness is still architectural: any key delivered to the browser for client-side encryption can be observed, replayed, and modeled.

## 5. Advanced Bypass Techniques
* **Monkey Patching the Crypto Engine:** Instead of reversing the whole logic, hook the crypto library in the browser console.
  ```javascript
  // Example: Hooking AES-GCM
  const originalEncrypt = window.crypto.subtle.encrypt;
  window.crypto.subtle.encrypt = function(algo, key, data) {
      console.log("Captured Plaintext:", new TextDecoder().decode(data));
      return originalEncrypt.apply(this, arguments);
  };
  ```

* **Dependency Analysis:** Search for package.json in the leaked `.git` directory. If they use crypto-js, look up the exact version. Older versions may have documented cryptographic implementation weaknesses.

## 6. Why "Novel" Encryption Fails
The engineering flaw is almost always the lack of server-side secret validation. Developers assume that because the data arrived encrypted, the client must have used the correct key. Often, the server simply decrypts whatever the client sends, trusting the client's self-generated IV (Initialization Vector). This is the golden path for manipulation.

Jericho Framework: Mapping the developer's logic to your exploit.
