# Copyright (c) Microsoft. All rights reserved.
"""Unit tests for SecurityHeadersMiddleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.middleware.security_headers import SecurityHeadersMiddleware


@pytest.fixture
def app_with_security_headers():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    return app


def test_security_headers_present(app_with_security_headers):
    client = TestClient(app_with_security_headers)
    response = client.get("/test")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
