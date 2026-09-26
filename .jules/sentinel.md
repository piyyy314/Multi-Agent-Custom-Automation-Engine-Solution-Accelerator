## 2026-03-31 - Exception Detail Leakage in FastAPI Endpoints
**Vulnerability:** Internal exception strings (`str(e)`) were being passed directly into `HTTPException` detail responses across multiple API router endpoints, leaking internal server error messages and database details to client callers.
**Learning:** Returning exception strings in HTTP error details for developer convenience can inadvertently expose backend implementation details, configuration issues, or internal database errors.
**Prevention:** Always log full exception details on the server side using `logger.error("...", exc_info=True)` and return sanitized, generic error detail messages to the client in `HTTPException`.
