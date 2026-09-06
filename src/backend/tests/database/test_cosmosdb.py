import pytest
from unittest.mock import AsyncMock, patch
from common.database.cosmosdb import CosmosDBClient
from common.models.messages_af import Plan, DataType


@pytest.mark.asyncio
async def test_get_plan_by_plan_id_includes_user_id_filter():
    """Verify that get_plan_by_plan_id includes user_id in the SQL query for user isolation (IDOR protection)."""
    user_id = "test-user-123"
    plan_id = "plan-456"

    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock-key",
        database_name="mock-db",
        container_name="mock-container",
        user_id=user_id,
    )

    mock_plan = Plan(
        id=plan_id,
        plan_id=plan_id,
        user_id=user_id,
        session_id="session-789",
        team_id="team-1",
        initial_goal="Test goal",
    )

    with patch.object(client, "query_items", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = [mock_plan]

        result = await client.get_plan_by_plan_id(plan_id)

        assert result == mock_plan
        assert mock_query.called
        call_args = mock_query.call_args
        query_str = call_args[0][0]
        parameters = call_args[0][1]

        # Verify that query filters by user_id
        assert "c.user_id=@user_id" in query_str
        # Verify that parameters contain user_id
        assert {"name": "@user_id", "value": user_id} in parameters
