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

## 2025-03-10 - Health Check Middleware Information Leak on Empty Password
**Vulnerability:**
When `HealthCheckMiddleware` was initialized with an empty password string (`password=""`), querying `/healthz?code=` caused `"" == ""` to evaluate to True, leaking detailed internal system health check results and exception messages to unauthenticated callers.

**Learning:**
`self.password is not None` evaluated to True for empty string passwords (`""`), allowing empty string `?code=` query parameters to bypass password protection. Furthermore, standard string equality (`==`) introduced potential timing side-channel risks.

**Prevention:**
1. Require `self.password` to be non-empty (`bool(self.password)`) before authorizing detailed health responses.
2. Use constant-time string comparison (`secrets.compare_digest`) for authorization token verification.
