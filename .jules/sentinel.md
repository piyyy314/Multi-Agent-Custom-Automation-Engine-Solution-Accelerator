## 2026-09-27 - Unauthenticated MCP Bridge Endpoints
**Vulnerability:** The `/clarification/ask` bridge endpoint accepted `user_id` directly from request bodies without verifying user principal authentication headers.
**Learning:** Endpoints serving as synchronous bridges between external/agent tools (like FastMCP tools) and user browser WebSocket sessions must validate user authentication headers (`get_authenticated_user_details`) to prevent unauthenticated injection into user sessions.
**Prevention:** Always enforce user principal authentication on all HTTP endpoints exposed by the API router.
