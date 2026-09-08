import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from common.database.cosmosdb import CosmosDBClient


class AsyncIterator:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)


@pytest.mark.asyncio
async def test_get_plan_by_plan_id_includes_user_id_filter():
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential=None,
        database_name="mock_db",
        container_name="mock_container",
        user_id="user-123-abc",
    )
    client._initialized = True
    client.container = MagicMock()

    with patch.object(client, "query_items", new_callable=AsyncMock) as mock_query:
        mock_query.return_value = []
        await client.get_plan_by_plan_id("plan-456")

        mock_query.assert_called_once()
        query, parameters, model_class = mock_query.call_args[0]

        # Verify SQL query string includes user_id check to prevent IDOR / auth bypass
        assert "c.user_id=@user_id" in query
        assert "c.id=@plan_id" in query

        # Verify parameters include user_id
        param_names = [p["name"] for p in parameters]
        param_values = {p["name"]: p["value"] for p in parameters}
        assert "@user_id" in param_names
        assert param_values["@user_id"] == "user-123-abc"


@pytest.mark.asyncio
async def test_delete_plan_by_plan_id_includes_user_id_filter():
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential=None,
        database_name="mock_db",
        container_name="mock_container",
        user_id="user-123-abc",
    )
    client._initialized = True
    mock_container = MagicMock()
    # Mock container query_items return as async iterator
    mock_container.query_items.return_value = AsyncIterator([])
    client.container = mock_container

    await client.delete_plan_by_plan_id("plan-789")

    mock_container.query_items.assert_called_once()
    kwargs = mock_container.query_items.call_args[1]
    query = kwargs.get("query")
    params = kwargs.get("parameters")

    assert "c.user_id=@user_id" in query
    assert "c.id=@plan_id" in query

    param_values = {p["name"]: p["value"] for p in params}
    assert param_values["@user_id"] == "user-123-abc"
