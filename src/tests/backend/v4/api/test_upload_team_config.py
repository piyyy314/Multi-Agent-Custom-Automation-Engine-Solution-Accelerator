import io
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from v4.api.router import app_v4

app = FastAPI()
app.include_router(app_v4)
client = TestClient(app)

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
AUTH_HEADERS = {"x-ms-client-principal-id": TEST_USER_ID}


def test_upload_team_config_invalid_extension():
    """Test uploading a file with non-JSON extension returns 400."""
    with patch("v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": TEST_USER_ID}), \
         patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        files = {"file": ("config.txt", io.BytesIO(b'{"name": "test"}'), "text/plain")}
        response = client.post("/api/v4/upload_team_config", files=files, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert response.json()["detail"] == "File must be a JSON file"


def test_upload_team_config_file_too_large():
    """Test uploading a file larger than 10MB returns 413 Payload Too Large."""
    # Create content larger than 10MB
    large_content = b"a" * (10 * 1024 * 1024 + 100)

    with patch("v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": TEST_USER_ID}), \
         patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        files = {"file": ("config.json", io.BytesIO(large_content), "application/json")}
        response = client.post("/api/v4/upload_team_config", files=files, headers=AUTH_HEADERS)

        assert response.status_code == 413
        assert response.json()["detail"] == "File size exceeds maximum allowed limit of 10MB"


def test_upload_team_config_valid_size_invalid_json():
    """Test uploading a file within size limit but with invalid JSON returns 400."""
    invalid_json_content = b"not valid json"

    with patch("v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": TEST_USER_ID}), \
         patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        files = {"file": ("config.json", io.BytesIO(invalid_json_content), "application/json")}
        response = client.post("/api/v4/upload_team_config", files=files, headers=AUTH_HEADERS)

        assert response.status_code == 400
        assert "Invalid JSON format" in response.json()["detail"]
