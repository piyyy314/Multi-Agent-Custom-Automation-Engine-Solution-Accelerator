import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Mock environment variables before importing app
os.environ["COSMOSDB_ENDPOINT"] = "https://mock-endpoint:443/"
os.environ["COSMOSDB_KEY"] = "mock-key"
os.environ["COSMOSDB_DATABASE"] = "mock-database"
os.environ["COSMOSDB_CONTAINER"] = "mock-container"
os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = (
    "InstrumentationKey=00000000-0000-0000-0000-000000000000;"
    "IngestionEndpoint=https://eastus-0.in.applicationinsights.azure.com/"
)
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "mock-deployment-name"
os.environ["AZURE_OPENAI_API_VERSION"] = "2023-01-01"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://mock-openai-endpoint"
os.environ["AZURE_AI_SUBSCRIPTION_ID"] = "00000000-0000-0000-0000-000000000000"
os.environ["AZURE_AI_RESOURCE_GROUP"] = "rg-test"
os.environ["AZURE_AI_PROJECT_NAME"] = "proj-test"
os.environ["AZURE_AI_AGENT_ENDPOINT"] = "https://agents.example.com/"

# Ensure repo root and src/backend are on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

with patch("azure.monitor.opentelemetry.configure_azure_monitor", MagicMock()):
    from app import app

client = TestClient(app)


def test_websocket_auth_header_overrides_query_param():
    """Test that WebSocket authentication headers override unauthenticated query param user_id."""
    headers = {"x-ms-client-principal-id": "authenticated_user_789"}

    with patch("v4.api.router.connection_config.add_connection") as mock_add_conn, \
         patch("v4.api.router.connection_config.close_connection") as mock_close_conn, \
         patch("v4.api.router.DatabaseFactory.get_database") as mock_db:

        mock_memory = MagicMock()
        mock_db.return_value = mock_memory

        with client.websocket_connect("/api/v4/socket/process_123?user_id=spoofed_user_999", headers=headers):
            pass

        # Verify add_connection was called with authenticated user_id from headers ('authenticated_user_789'), not spoofed query param ('spoofed_user_999')
        mock_add_conn.assert_called_once()
        _, kwargs = mock_add_conn.call_args
        assert kwargs["user_id"] == "authenticated_user_789"
        assert kwargs["process_id"] == "process_123"


def test_upload_team_config_invalid_file_extension():
    """Test that upload_team_config handles non-json extension gracefully with HTTP 400."""
    headers = {"x-ms-client-principal-id": "authenticated_user_123"}
    files = {"file": ("config.txt", b"{}", "text/plain")}

    with patch("v4.api.router.DatabaseFactory.get_database"):
        response = client.post("/api/v4/upload_team_config", files=files, headers=headers)
        assert response.status_code == 400
        assert "File must be a JSON file" in response.json()["detail"]
