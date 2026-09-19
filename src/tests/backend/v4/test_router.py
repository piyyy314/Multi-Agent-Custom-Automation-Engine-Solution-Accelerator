from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException, UploadFile
from v4.api.router import upload_team_config


@pytest.mark.asyncio
async def test_upload_team_config_exceeds_max_size():
    """Test that uploading a file exceeding 5MB raises HTTPException 413."""
    mock_request = MagicMock()
    mock_request.headers = {"x-ms-client-principal-id": "test-user-id"}

    large_content = b"x" * (5 * 1024 * 1024 + 1)
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "config.json"
    mock_file.read.return_value = large_content

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await upload_team_config(request=mock_request, file=mock_file)

        assert exc_info.value.status_code == 413
        assert "exceeds the maximum allowed limit" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_team_config_invalid_extension():
    """Test that uploading a non-JSON file raises HTTPException 400."""
    mock_request = MagicMock()
    mock_request.headers = {"x-ms-client-principal-id": "test-user-id"}

    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "config.txt"

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await upload_team_config(request=mock_request, file=mock_file)

        assert exc_info.value.status_code == 400
        assert "File must be a JSON file" in exc_info.value.detail


@pytest.mark.asyncio
async def test_upload_team_config_path_traversal_filename():
    """Test that path traversal in filenames is sanitized."""
    mock_request = MagicMock()
    mock_request.headers = {"x-ms-client-principal-id": "test-user-id"}

    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "../../etc/passwd.json"
    mock_file.read.return_value = b"invalid json"

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await upload_team_config(request=mock_request, file=mock_file)

        # Should pass filename check and fail on JSON format (400)
        assert exc_info.value.status_code == 400
        assert "Invalid JSON format" in exc_info.value.detail
