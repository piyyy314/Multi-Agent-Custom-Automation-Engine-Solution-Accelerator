# Sentinel's Security Journal

## 2025-03-05 - Secure Health Check Middleware Validation
**Vulnerability:** The health check middleware (`HealthCheckMiddleware`) allowed exposing detailed JSON health status metrics (including system/database connection details and stack traces/exceptions) when the authentication password was unconfigured (None, empty string `""`, or only whitespaces `"   "`), as any matching empty query parameter `code=` bypassed authentication. Additionally, the string comparison for the security code was performed using the standard equality operator (`==`), which is vulnerable to timing attacks (CWE-208).
**Learning:** String comparison vulnerability existed because the default string equality operator (`==`) optimizes comparison speed by returning early on the first mismatched character, creating a timing side-channel. The open disclosure risk existed because the presence of the `code` query parameter was checked against the configured password without ensuring the password itself was configured and non-empty.
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

## 2025-03-29 - CosmosDB Query User ID Filter Omission (IDOR)
**Vulnerability:**
In `CosmosDBClient.get_plan_by_plan_id`, the SQL query string `SELECT * FROM c WHERE c.id=@plan_id AND c.data_type=@data_type` omitted `c.user_id=@user_id` despite including `@user_id` in the query parameter dictionary. This allowed cross-user access to execution plans via `plan_id`.

**Learning:**
Passing `user_id` in query parameters does not enforce authorization if the SQL string itself omits the corresponding `WHERE` clause condition.

**Prevention:**
Ensure every parameter supplied in database query parameter maps is explicitly referenced and enforced in SQL `WHERE` clauses for tenant and user isolation.
