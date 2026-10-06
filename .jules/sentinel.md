## 2026-03-31 - Missing Authentication and IDOR on MCP Bridge Endpoint
**Vulnerability:** The `/clarification/ask` endpoint, used as a synchronous bridge for MCP `ask_user`, did not perform authentication or validate that the provided `user_id` matched the caller's identity, allowing unauthenticated requests and user impersonation.
**Learning:** Internal bridge or callback endpoints added for tooling integration (like MCP servers) can easily be overlooked during security checks if they bypass standard header-based authentication patterns.
**Prevention:** Always enforce `get_authenticated_user_details(request_headers=request.headers)` on every API route and ensure `user_id` is derived directly from or strictly validated against `auth_user_id`.
