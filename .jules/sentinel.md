## 2025-05-20 - Restrict CORS Origins when Credentials are Allowed
**Vulnerability:** In `src/backend/app.py`, `CORSMiddleware` was configured with `allow_origins=["*"]` while `allow_credentials=True`. This allowed any malicious site in a user's browser to make authenticated cross-origin requests to the backend API.
**Learning:** Combining wildcard origins (`*`) with `allow_credentials=True` creates a CORS vulnerability that bypasses browser same-origin policy protections for credentialed HTTP requests (cookies, authorization headers, or client certificates).
**Prevention:** Always restrict `allow_origins` to explicitly configured domain(s) (e.g. `[frontend_url]`) when credentials are allowed in CORS middleware.
