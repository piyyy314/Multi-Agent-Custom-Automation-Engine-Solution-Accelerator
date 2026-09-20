"""
Security unit tests for API router exception response sanitization.
Verifies that internal database or infrastructure exceptions do not leak internal details to clients.
"""

import os
import sys
import pytest
from unittest.mock import patch, NonCallableMock

# Ensure src root is on sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Skip if v4 or v4.models has been mocked by another test file during test collection
_v4_is_mocked = ('v4' in sys.modules and isinstance(sys.modules['v4'], NonCallableMock)) or \
                ('v4.models' in sys.modules and isinstance(sys.modules['v4.models'], NonCallableMock))
if _v4_is_mocked:
    pytest.skip(
        "Skipping test_router_security.py: v4 module has been mocked by another test file.",
        allow_module_level=True
    )

from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.v4.api.router import app_v4

test_app = FastAPI()
test_app.include_router(app_v4)
client = TestClient(test_app)

AUTH_HEADERS = {"x-ms-client-principal-id": "test-security-user-123"}


class TestRouterSecurityErrorSanitization:
    """Tests ensuring exceptions in v4 API endpoints do not leak internal exception details."""

    def test_init_team_sanitizes_exception_details(self):
        """Test init_team does not leak internal exception message in HTTP response."""
        sensitive_error_msg = "Sensitive DB Secret Connection String Error"
        with patch("backend.v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-123"}), \
             patch("backend.v4.api.router.DatabaseFactory.get_database", side_effect=RuntimeError(sensitive_error_msg)):
            response = client.get("/api/v4/init_team", headers=AUTH_HEADERS)
            assert response.status_code == 400
            detail = response.json().get("detail", "")
            assert sensitive_error_msg not in detail
            assert detail == "Error starting request"

    def test_process_request_sanitizes_exception_details(self):
        """Test process_request does not leak internal exception message when retrieving team configuration."""
        sensitive_error_msg = "Sensitive Internal Infrastructure Exception"
        with patch("backend.v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-123"}), \
             patch("backend.v4.api.router.DatabaseFactory.get_database", side_effect=RuntimeError(sensitive_error_msg)):
            payload = {"session_id": "sess-1", "description": "Test task"}
            response = client.post("/api/v4/process_request", json=payload, headers=AUTH_HEADERS)
            assert response.status_code == 400
            detail = response.json().get("detail", "")
            assert sensitive_error_msg not in detail
            assert detail == "Error retrieving team configuration"

    def test_user_clarification_sanitizes_exception_details(self):
        """Test user_clarification does not leak internal exception message."""
        sensitive_error_msg = "Database Password Failed Exception"
        with patch("backend.v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-123"}), \
             patch("backend.v4.api.router.DatabaseFactory.get_database", side_effect=RuntimeError(sensitive_error_msg)):
            payload = {"request_id": "req-1", "answer": "Clarification text"}
            response = client.post("/api/v4/user_clarification", json=payload, headers=AUTH_HEADERS)
            assert response.status_code == 400
            detail = response.json().get("detail", "")
            assert sensitive_error_msg not in detail
            assert detail == "Error retrieving team configuration"

    def test_upload_team_config_sanitizes_exception_details(self):
        """Test upload_team_config does not leak internal exception message."""
        sensitive_error_msg = "Internal CosmosDB Credentials Invalid Exception"
        with patch("backend.v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-123"}), \
             patch("backend.v4.api.router.DatabaseFactory.get_database", side_effect=RuntimeError(sensitive_error_msg)):
            files = {"file": ("team.json", b'{"name": "Team"}', "application/json")}
            response = client.post("/api/v4/upload_team_config", files=files, headers=AUTH_HEADERS)
            assert response.status_code == 400
            detail = response.json().get("detail", "")
            assert sensitive_error_msg not in detail
            assert detail == "Error retrieving team configuration"
