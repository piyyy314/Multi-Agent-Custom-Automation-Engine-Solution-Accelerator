import io
import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from v4.api.router import app_v4

router_app = FastAPI()
router_app.include_router(app_v4)
client = TestClient(router_app)

@pytest.mark.asyncio
async def test_upload_team_config_sanitizes_value_error():
    """Test that upload_team_config returns a sanitized error detail on ValueError without leaking internal details."""
    invalid_json = json.dumps({"name": "Test Team"}).encode("utf-8")
    file_payload = ("team.json", io.BytesIO(invalid_json), "application/json")

    with patch("v4.api.router.DatabaseFactory.get_database", new_callable=AsyncMock) as mock_db_factory, \
         patch("v4.api.router.rai_validate_team_config", new_callable=AsyncMock) as mock_rai, \
         patch("v4.api.router.TeamService") as mock_team_service_cls:

        mock_rai.return_value = (True, None)
        mock_team_service_instance = AsyncMock()
        mock_team_service_instance.validate_team_models.return_value = (True, [])
        mock_team_service_instance.validate_team_search_indexes.return_value = (True, [])
        # Simulate a ValueError containing internal details/stack info during configuration validation
        mock_team_service_instance.validate_and_parse_team_config.side_effect = ValueError(
            "Sensitive internal validation details: secret_key_123 invalid format at line 42"
        )
        mock_team_service_cls.return_value = mock_team_service_instance

        headers = {"x-ms-client-principal-id": "test-user-id"}
        response = client.post(
            "/api/v4/upload_team_config",
            files={"file": file_payload},
            headers=headers,
        )

        assert response.status_code == 400
        response_json = response.json()
        assert response_json["detail"] == "Invalid team configuration format"
        assert "secret_key_123" not in response_json["detail"]
