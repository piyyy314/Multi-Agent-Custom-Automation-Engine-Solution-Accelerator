import io
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request, UploadFile
from v4.api.router import upload_team_config


@pytest.mark.asyncio
async def test_upload_team_config_missing_filename():
    """Test upload_team_config with filename=None raises 400 Bad Request."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"x-ms-client-principal-id": "test-user-id"}

    upload_file = UploadFile(filename=None, file=io.BytesIO(b'{"name": "test"}'))

    with patch("v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-id"}), \
         patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await upload_team_config(request=mock_request, file=upload_file)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "File must be a JSON file"


@pytest.mark.asyncio
async def test_upload_team_config_invalid_extension():
    """Test upload_team_config with non-json extension raises 400 Bad Request."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"x-ms-client-principal-id": "test-user-id"}

    upload_file = UploadFile(filename="config.txt", file=io.BytesIO(b'{"name": "test"}'))

    with patch("v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-id"}), \
         patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await upload_team_config(request=mock_request, file=upload_file)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "File must be a JSON file"


@pytest.mark.asyncio
async def test_upload_team_config_exceeds_max_size():
    """Test upload_team_config with payload exceeding 5MB raises 400 Bad Request."""
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"x-ms-client-principal-id": "test-user-id"}

    large_content = b"a" * (5 * 1024 * 1024 + 1)
    upload_file = UploadFile(filename="config.json", file=io.BytesIO(large_content))

    with patch("v4.api.router.get_authenticated_user_details", return_value={"user_principal_id": "test-user-id"}), \
         patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await upload_team_config(request=mock_request, file=upload_file)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "File size exceeds maximum allowed limit of 5MB"
