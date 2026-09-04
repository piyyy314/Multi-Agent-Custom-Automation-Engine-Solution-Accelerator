import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_upload_team_config_oversized_file():
    """Test that file uploads exceeding 2MB are rejected with 413 Payload Too Large."""
    # Create mock memory database and mock auth headers
    mock_headers = {"x-ms-client-principal-id": "test-user-123"}

    # 2MB + 100 bytes payload
    oversized_data = b"a" * (2 * 1024 * 1024 + 100)
    files = {"file": ("large_config.json", oversized_data, "application/json")}

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = AsyncMock()
        response = client.post(
            "/api/v4/upload_team_config",
            files=files,
            headers=mock_headers,
        )

    assert response.status_code == 413
    assert "exceeds maximum allowed limit of 2MB" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_team_config_invalid_extension():
    """Test that file uploads with non-JSON extension or missing filename are rejected with 400."""
    mock_headers = {"x-ms-client-principal-id": "test-user-123"}
    files = {"file": ("config.txt", b"{}", "text/plain")}

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = AsyncMock()
        response = client.post(
            "/api/v4/upload_team_config",
            files=files,
            headers=mock_headers,
        )

    assert response.status_code == 400
    assert "valid JSON file" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_team_config_invalid_json():
    """Test that invalid JSON payload returns generic error message without exposing stack details."""
    mock_headers = {"x-ms-client-principal-id": "test-user-123"}
    files = {"file": ("invalid.json", b"{invalid-json", "application/json")}

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock) as mock_db:
        mock_db.return_value = AsyncMock()
        response = client.post(
            "/api/v4/upload_team_config",
            files=files,
            headers=mock_headers,
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON format in configuration file"
