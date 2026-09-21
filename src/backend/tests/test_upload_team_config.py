from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import pytest

from app import app

client = TestClient(app)

UPLOAD_URL = "/api/v4/upload_team_config"


@pytest.mark.asyncio
async def test_upload_team_config_file_too_large():
    """Test that uploading a file larger than 5MB is rejected with 400 Bad Request."""
    headers = {"x-ms-client-principal-id": "test-user-123"}
    # Create content larger than 5MB
    large_content = b"a" * (5 * 1024 * 1024 + 1)
    files = {"file": ("large_team.json", large_content, "application/json")}

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        response = client.post(UPLOAD_URL, files=files, headers=headers)

    assert response.status_code == 400
    assert "File size exceeds maximum allowed limit of 5MB" in response.json()["detail"]
