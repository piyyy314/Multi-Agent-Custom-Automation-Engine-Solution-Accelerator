## 2026-10-07 - Environment-Aware CORS Origin Restriction
**Vulnerability:** Permissive CORS configuration with wildcard origins (`"*"`) allowed credentials and cross-origin access across all environments.
**Learning:** In production environments, combining `allow_credentials=True` with wildcard origins creates cross-origin security exposure. Restricting allowed origins to configured trusted site endpoints (`config.FRONTEND_SITE_NAME`) in non-dev environments hardens the application against cross-origin data exposure.
**Prevention:** Always restrict `CORSMiddleware` `allow_origins` to explicitly trusted frontend domains in non-dev/production environments.

## 2026-10-14 - Environment-Aware Authentication Fallback
**Vulnerability:** Defaulting missing EasyAuth headers (`x-ms-client-principal-id`) to `sample_user` allowed unauthenticated requests to bypass authentication and assume sample user privileges in production environments.
**Learning:** Development authentication fallbacks must be strictly gated by environment configuration (`config.APP_ENV == "dev"`). Returning empty principal details in non-dev environments causes unauthenticated HTTP requests to fail safely with 400/401 errors.
**Prevention:** Always verify `APP_ENV == "dev"` before applying dev-only sample credentials or bypass logic.
