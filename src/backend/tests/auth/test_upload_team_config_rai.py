import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

SAMPLE_TEAM_CONFIG = {
    "name": "Test Team",
    "status": "active",
    "agents": [
        {
            "input_key": "agent1",
            "type": "standard",
            "name": "Agent One",
            "icon": "icon.png",
            "description": "An agent"
        }
    ],
    "starting_tasks": [
        {
            "id": "task1",
            "name": "Task One",
            "prompt": "Do task",
            "created": "2025-01-01",
            "creator": "admin",
            "logo": "logo.png"
        }
    ]
}


@patch("v4.api.router.rai_validate_team_config", new_callable=AsyncMock)
@patch("v4.api.router.get_authenticated_user_details")
def test_upload_team_config_without_team_id_rai_failure(
    mock_get_user, mock_rai_validate
):
    mock_get_user.return_value = {"user_principal_id": "test-user-id"}
    mock_rai_validate.return_value = (
        False,
        "Team configuration contains inappropriate content and cannot be uploaded.",
    )

    file_bytes = json.dumps(SAMPLE_TEAM_CONFIG).encode("utf-8")
    files = {"file": ("team_config.json", file_bytes, "application/json")}

    response = client.post("/api/v4/upload_team_config", files=files)

    assert response.status_code == 400
    assert (
        "Team configuration contains inappropriate content" in response.json()["detail"]
    )
    mock_rai_validate.assert_called_once()


@patch("v4.api.router.rai_validate_team_config", new_callable=AsyncMock)
@patch("v4.api.router.get_authenticated_user_details")
def test_upload_team_config_with_team_id_rai_failure(
    mock_get_user, mock_rai_validate
):
    mock_get_user.return_value = {"user_principal_id": "test-user-id"}
    mock_rai_validate.return_value = (
        False,
        "Team configuration contains inappropriate content and cannot be uploaded.",
    )

    file_bytes = json.dumps(SAMPLE_TEAM_CONFIG).encode("utf-8")
    files = {"file": ("team_config.json", file_bytes, "application/json")}

    response = client.post(
        "/api/v4/upload_team_config?team_id=existing-team-id", files=files
    )

    assert response.status_code == 400
    assert (
        "Team configuration contains inappropriate content" in response.json()["detail"]
    )
    mock_rai_validate.assert_called_once()
