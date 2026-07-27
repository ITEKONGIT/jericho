# Password Reset Logic

Password reset flows are often treated as support plumbing instead of authentication-critical code. In practice, they are one of the best places to find weak OTPs, account enumeration, broken identity binding, stale sessions, and leaked reset material.

## 1. Four Digit OTPs

Four digit OTPs are still widely deployed. The issue is not only the small keyspace; it is usually the weak handling around the code.

Check for:

* No rate limit per account, IP, device, phone number, and reset transaction.
* No lockout or delay after repeated failures.
* OTP reuse after successful verification.
* OTP valid across multiple users or reset attempts.
* OTP remains valid after requesting a new one.
* OTP has a long expiry window.
* Different errors for valid account, invalid account, wrong OTP, expired OTP, and already-used OTP.
* Missing binding between OTP, reset transaction id, user id, phone number, and purpose.

Secure pattern:

* Prefer 6 or more digits, or a high-entropy reset token.
* Bind the OTP to one account, one delivery target, one reset transaction, and one purpose.
* Expire it quickly.
* Burn it after one successful or terminal use.
* Rate limit verification and resend independently.
* Return generic errors.

## 2. Identity Binding Bugs

Many reset flows ask for multiple identifiers: username, email, phone number, customer id, or tenant id. The dangerous bug is partial validation.

Example weak flow:

```text
POST /forgot-password
{
  "username": "victim",
  "phone": "+15551234567"
}
```

The backend verifies that `username` exists, but does not verify that `phone` belongs to that username. The OTP is then sent to the supplied phone number, allowing account takeover if the next step trusts the OTP.

Assess:

* Does the flow accept username plus phone number?
* Does it accept username plus email?
* Does it accept phone number alone?
* Does changing the phone or email still trigger an OTP?
* Is the delivery target selected by the user input or by the account record?
* Is the reset transaction tied to the account before OTP delivery?
* Can the username be valid while the phone/email belongs to another account?
* Does the next step rely only on OTP and not the original verified account binding?

Secure pattern:

* Use the submitted identifier only to locate the account.
* Send recovery material only to a verified contact already attached to that account.
* Store a reset transaction id tied to the account id and delivery channel.
* On every step, validate the same transaction id, same account id, same delivery target, and same purpose.

## 3. Forgot Password Response Leakage

Some forgot-password endpoints return reset material in the response. Developers may think this is safe if the value is hashed, encrypted, masked, or only returned in non-production paths.

Watch for responses containing:

* OTP values.
* Reset tokens.
* Hashed OTPs.
* Encrypted OTPs.
* Password reset URLs.
* User ids, recovery ids, or reset transaction ids that are not meant for the client.
* Flags such as `otpSent`, `otpHash`, `forgotPasswordToken`, `resetPasswordValue`, or `passwordResetCode`.

Why hashed or encrypted reset values still matter:

* The app may compare client-supplied hashes instead of server-side OTP values.
* The encrypted value may be decryptable from frontend code or mobile code.
* The value may be replayable as a bearer reset artifact.
* It may reveal whether the account exists.

Secure pattern:

* Never return OTPs, reset tokens, hashes, encrypted reset values, or delivery secrets to the client.
* Store reset material server-side.
* Return only a generic status such as `If the account exists, recovery instructions were sent.`

## 4. Session Handling After Reset

Password reset should invalidate existing sessions and refresh tokens. If it does not, account recovery only changes the password while stolen sessions continue working.

Check:

* Are old access tokens still accepted after reset?
* Are old refresh tokens still accepted after reset?
* Are mobile sessions still active?
* Are WebSocket or long-lived sessions disconnected?
* Does MFA reset or email change also invalidate sessions?

Secure pattern:

* Increment a user session version on reset.
* Revoke refresh tokens.
* Require re-authentication on active sessions.
* Log and notify the user of recovery events.

Use only on systems where you have authorization to test.
