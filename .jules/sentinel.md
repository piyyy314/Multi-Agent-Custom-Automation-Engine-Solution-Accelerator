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

## 2025-03-27 - IDOR via Unreferenced Query Parameters in CosmosDB Queries
**Vulnerability:**
`CosmosDBClient.get_plan_by_plan_id` prepared `@user_id` in its parameter array (`parameters = [{"name": "@user_id", "value": self.user_id}, ...]`), but omitted `AND c.user_id=@user_id` from the SQL string (`WHERE c.id=@plan_id AND c.data_type=@data_type`). This allowed any user knowing a `plan_id` to retrieve another user's plan.

**Learning:**
Supplying query parameters to database drivers does not enforce filtering unless the parameter is explicitly referenced in the SQL `WHERE` clause.

**Prevention:**
Always verify that all user context parameters passed to parameterized database calls are explicitly bound in the SQL query string.
