## 2026-10-07 - Environment-Aware CORS Origin Restriction
**Vulnerability:** Permissive CORS configuration with wildcard origins (`"*"`) allowed credentials and cross-origin access across all environments.
**Learning:** In production environments, combining `allow_credentials=True` with wildcard origins creates cross-origin security exposure. Restricting allowed origins to configured trusted site endpoints (`config.FRONTEND_SITE_NAME`) in non-dev environments hardens the application against cross-origin data exposure.
**Prevention:** Always restrict `CORSMiddleware` `allow_origins` to explicitly trusted frontend domains in non-dev/production environments.
