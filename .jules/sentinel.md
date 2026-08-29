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
1. Restrict CORS allowed origins dynamically based on the configured frontend URL and local development origins, rejecting wildcards when credentials are enabled.
2. Enforce strict environment-based guards (`APP_ENV == "dev"`) before returning default or mock users, failing securely on missing principal headers in non-development environments.

## 2025-05-15 - Missing User ID Filter in CosmosDB Queries (BOLA / IDOR)
**Vulnerability:**
1. Several query methods in `CosmosDBClient` (`get_plan_by_plan_id`, `delete_plan_by_plan_id`, `get_mplan`, `get_agent_messages`, `get_steps_by_plan`, `get_step`, etc.) omitted `c.user_id=@user_id` from their SQL query strings despite `@user_id` being passed in the parameter list.
2. This created a Broken Object Level Authorization (BOLA / IDOR) vulnerability, allowing an authenticated user to query or delete another user's plans, steps, and agent messages if the ID was known or guessed.

**Learning:**
1. Developer intention was to filter by user ID (as evidenced by `@user_id` being included in `parameters`), but the SQL WHERE clause `c.user_id=@user_id` was accidentally omitted from the query string.
2. CosmosDB ignores unused query parameters silently, leading to queries succeeding without applying the intended user isolation predicate.

**Prevention:**
1. Explicitly verify that every CosmosDB SQL query includes `c.user_id=@user_id` when accessing user-scoped resources.
2. Add unit tests asserting that SQL query strings contain user isolation predicates and pass corresponding parameters.
