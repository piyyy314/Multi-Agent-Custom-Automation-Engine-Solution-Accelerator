import os

# Provide default env vars
os.environ.setdefault("COSMOSDB_ENDPOINT", "https://mock.documents.azure.com:443/")
os.environ.setdefault("COSMOSDB_KEY", "mock-key")
os.environ.setdefault("COSMOSDB_DATABASE", "mock-database")
os.environ.setdefault("COSMOSDB_CONTAINER", "mock-container")
os.environ.setdefault(
    "APPLICATIONINSIGHTS_CONNECTION_STRING",
    "InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://eastus-0.in.applicationinsights.azure.com/",
)
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://mock.openai.azure.com")
os.environ.setdefault("AZURE_AI_SUBSCRIPTION_ID", "mock-sub")
os.environ.setdefault("AZURE_AI_RESOURCE_GROUP", "mock-rg")
os.environ.setdefault("AZURE_AI_PROJECT_NAME", "mock-proj")
os.environ.setdefault("AZURE_AI_AGENT_ENDPOINT", "https://mock.agent.azure.com")

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from v4.api.router import app_v4

app_for_test = FastAPI()
app_for_test.include_router(app_v4)

client = TestClient(app_for_test)


@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    """Mock authentication user details."""
    monkeypatch.setattr(
        "auth.auth_utils.get_authenticated_user_details",
        lambda request_headers: {"user_principal_id": "mock-user-123"},
    )


def test_upload_team_config_exceeds_max_file_size():
    """Test that uploading a file larger than 5MB returns HTTP 413 Payload Too Large."""
    # Create oversized content (> 5 MB)
    oversized_content = b"{" + b'"a": "' + (b"x" * (5 * 1024 * 1024 + 10)) + b'"}'
    files = {"file": ("large_team_config.json", oversized_content, "application/json")}
    headers = {"x-ms-client-principal-id": "mock-user-123"}

    response = client.post("/api/v4/upload_team_config", files=files, headers=headers)

    assert response.status_code == 413
    data = response.json()
    assert "File size exceeds maximum allowed limit of 5MB" in data.get("detail", "")


def test_upload_team_config_within_max_file_size():
    """Test that a file under 5MB passes size validation."""
    valid_size_content = b'{"name": "Test Team"}'
    files = {"file": ("valid_team_config.json", valid_size_content, "application/json")}
    headers = {"x-ms-client-principal-id": "mock-user-123"}

    response = client.post("/api/v4/upload_team_config", files=files, headers=headers)

    # Should pass size validation (status code will not be 413)
    assert response.status_code != 413
