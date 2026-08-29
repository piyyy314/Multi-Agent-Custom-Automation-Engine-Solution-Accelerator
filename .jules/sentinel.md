# Sentinel Journal 🛡️

This journal records critical security-focused learnings discovered in the codebase, highlighting vulnerabilities, their root causes, and prevention strategies.

## 2025-03-10 - Overly Permissive CORS and Production Auth Fallback
**Vulnerability:**
1. Overly permissive CORS configuration (`allow_origins=["*"]`) used in conjunction with `allow_credentials=True`. This is a security risk allowing cross-origin credential sharing, and also a functional issue since compliant browsers block wildcards when credentials are allowed.
2. Unauthenticated fallback logic in `get_authenticated_user_details` which falls back to a default `sample_user` profile when authentication headers are absent, irrespective of the current environment (even in production).

**Learning:**
1. CORS policies were set to wildcard origins for local development convenience, but were not restricted for production environments, leaving credentialed requests exposed.
2. The authentication middleware assumed that if `x-ms-client-principal-id` was missing, the application was running in development mode, neglecting cases where EasyAuth is misconfigured, disabled, or bypassed in production.

**Prevention:**
1. Restrict CORS allowed origins dynamically based on the configured frontend URL and local development origins, rejecting wildcards when credentials are enabled.
2. Enforce strict environment-based guards (`APP_ENV == "dev"`) before returning default or mock users, failing securely on missing principal headers in non-development environments.

## 2025-05-18 - Unprotected Health Check Details via Empty Password Matching & Non-Constant-Time Password Check
**Vulnerability:**
1. `HealthCheckMiddleware` checked `self.password is not None`, which allowed an empty string password (`password=""`) to match `GET /healthz?code=`, exposing internal system health details and stack exceptions in JSON format to unauthenticated users.
2. Direct string equality comparison (`==`) was used for secret/access code comparison, introducing potential timing attack vulnerabilities.

**Learning:**
1. Using `is not None` to check if a password parameter is configured allowed empty password strings to be considered "configured", making empty query parameters match empty secrets.
2. Security-sensitive string comparisons were performed without constant-time comparison helpers.

**Prevention:**
1. Check `bool(self.password)` to ensure password authentication is only enabled when a non-empty secret is set.
2. Always use `hmac.compare_digest` for secret and authorization token comparisons to prevent timing side-channel attacks.
