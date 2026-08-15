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

## 2025-03-24 - Information Disclosure via Blank Middleware Passwords
**Vulnerability:**
`HealthCheckMiddleware` checked `if self.password is not None and request.query_params.get("code") == self.password`. When `password` was set to an empty string `""` (as in `app.py`), querying `/healthz?code=` resulted in `"" == ""`, granting unauthorized access to detailed JSON diagnostic check results.

**Learning:**
Checking `is not None` on configuration settings that default or fall back to empty strings can lead to unintended equality matches when query parameters are omitted or empty.

**Prevention:**
Always check truthiness (`if self.password and ...`) or validate that secret parameters are non-empty strings before using them in equality comparisons for authentication or authorization checks.
