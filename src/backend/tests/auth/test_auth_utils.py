import os
import sys

# Provide safe defaults for environment variables before any imports load config
os.environ.setdefault("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=mock")
os.environ.setdefault("AZURE_AI_SUBSCRIPTION_ID", "mock")
os.environ.setdefault("AZURE_AI_RESOURCE_GROUP", "mock")
os.environ.setdefault("AZURE_AI_PROJECT_NAME", "mock")
os.environ.setdefault("AZURE_AI_AGENT_ENDPOINT", "https://agents.example.com/")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://openai.example.com/")

from unittest.mock import patch, Mock
import base64
import json

from src.backend.auth.auth_utils import get_authenticated_user_details, get_tenantid


def test_get_authenticated_user_details_with_headers():
    """Test get_authenticated_user_details with valid headers."""
    request_headers = {
        "x-ms-client-principal-id": "test-user-id",
        "x-ms-client-principal-name": "test-user-name",
        "x-ms-client-principal-idp": "test-auth-provider",
        "x-ms-token-aad-id-token": "test-auth-token",
        "x-ms-client-principal": "test-client-principal-b64",
    }

    result = get_authenticated_user_details(request_headers)

    assert result["user_principal_id"] == "test-user-id"
    assert result["user_name"] == "test-user-name"
    assert result["auth_provider"] == "test-auth-provider"
    assert result["auth_token"] == "test-auth-token"
    assert result["client_principal_b64"] == "test-client-principal-b64"
    assert result["aad_id_token"] == "test-auth-token"


def test_get_tenantid_with_valid_b64():
    """Test get_tenantid with a valid base64-encoded JSON string."""
    valid_b64 = base64.b64encode(
        json.dumps({"tid": "test-tenant-id"}).encode("utf-8")
    ).decode("utf-8")

    tenant_id = get_tenantid(valid_b64)

    assert tenant_id == "test-tenant-id"


def test_get_tenantid_with_empty_b64():
    """Test get_tenantid with an empty base64 string."""
    tenant_id = get_tenantid("")
    assert tenant_id == ""


@patch("auth.auth_utils.logging.getLogger", return_value=Mock())
def test_get_tenantid_with_invalid_b64(mock_logger):
    """Test get_tenantid with an invalid base64-encoded string."""
    invalid_b64 = "invalid-base64"

    tenant_id = get_tenantid(invalid_b64)

    assert tenant_id == ""
    mock_logger().exception.assert_called_once()


def test_get_authenticated_user_details_no_headers_production():
    """Test get_authenticated_user_details in production environment with no auth headers."""
    with patch("common.config.app_config.config") as mock_config:
        mock_config.APP_ENV = "prod"
        request_headers = {}

        result = get_authenticated_user_details(request_headers)

        # Verify that it did not fall back to sample_user and instead returns empty/None details
        assert result.get("user_principal_id") is None
        assert result.get("user_name") is None


def test_get_authenticated_user_details_case_insensitive_headers():
    """Test get_authenticated_user_details with uppercase/mixed-case headers."""
    request_headers = {
        "X-MS-CLIENT-PRINCIPAL-ID": "uppercase-user-id",
        "X-MS-CLIENT-PRINCIPAL-NAME": "uppercase-user-name",
        "X-MS-CLIENT-PRINCIPAL-IDP": "uppercase-auth-provider",
        "X-MS-TOKEN-AAD-ID-TOKEN": "uppercase-auth-token",
        "X-MS-CLIENT-PRINCIPAL": "uppercase-client-principal-b64",
    }

    result = get_authenticated_user_details(request_headers)

    assert result["user_principal_id"] == "uppercase-user-id"
    assert result["user_name"] == "uppercase-user-name"
    assert result["auth_provider"] == "uppercase-auth-provider"
    assert result["auth_token"] == "uppercase-auth-token"
    assert result["client_principal_b64"] == "uppercase-client-principal-b64"
    assert result["aad_id_token"] == "uppercase-auth-token"
