# Sentinel's Security Journal

## 2025-03-05 - Secure Health Check Middleware Validation
**Vulnerability:** The health check middleware (`HealthCheckMiddleware`) allowed exposing detailed JSON health status metrics (including system/database connection details and stack traces/exceptions) when the authentication password was unconfigured (None, empty string `""`, or only whitespaces `"   "`), as any matching empty query parameter `code=` bypassed authentication. Additionally, the string comparison for the security code was performed using the standard equality operator (`==`), which is vulnerable to timing attacks (CWE-208).
**Learning:** String comparison vulnerability existed because the default string equality operator (`==`) optimizes comparison speed by returning early on the first mismatched character, creating a timing side-channel. The open disclosure risk existed because the presence of the `code` query parameter was checked against the configured password without ensuring the password itself was configured and non-empty.
**Prevention:**
1. Always use constant-time string comparison (`secrets.compare_digest`) for sensitive tokens, API keys, or security codes.
2. Explicitly validate that security/authentication passwords are not empty or blank before allowing them to match a request's credentials.
