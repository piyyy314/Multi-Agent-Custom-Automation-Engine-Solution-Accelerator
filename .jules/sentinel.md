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
