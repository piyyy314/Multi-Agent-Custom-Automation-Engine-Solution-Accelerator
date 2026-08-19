import pytest
from unittest.mock import AsyncMock, MagicMock
from common.database.cosmosdb import CosmosDBClient


@pytest.mark.asyncio
async def test_get_plan_by_plan_id_includes_user_id_clause():
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock",
        database_name="mockdb",
        container_name="mockcontainer",
        user_id="user_123",
    )
    client._initialized = True
    mock_container = MagicMock()
    mock_container.query_items = MagicMock(return_value=AsyncMock())
    client.container = mock_container

    # Mock query_items method on client
    captured_query = None
    captured_params = None

    async def mock_query_items(query, parameters, model_class):
        nonlocal captured_query, captured_params
        captured_query = query
        captured_params = parameters
        return []

    client.query_items = mock_query_items

    await client.get_plan_by_plan_id("plan_abc")

    assert captured_query is not None
    assert "c.user_id=@user_id" in captured_query
    user_id_param = next((p for p in captured_params if p.get("name") == "@user_id"), None)
    assert user_id_param is not None
    assert user_id_param.get("value") == "user_123"


@pytest.mark.asyncio
async def test_get_mplan_includes_user_id_clause():
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock",
        database_name="mockdb",
        container_name="mockcontainer",
        user_id="user_456",
    )
    client._initialized = True

    captured_query = None
    captured_params = None

    async def mock_query_items(query, parameters, model_class):
        nonlocal captured_query, captured_params
        captured_query = query
        captured_params = parameters
        return []

    client.query_items = mock_query_items

    await client.get_mplan("plan_def")

    assert captured_query is not None
    assert "c.user_id=@user_id" in captured_query
    user_id_param = next((p for p in captured_params if p.get("name") == "@user_id"), None)
    assert user_id_param is not None
    assert user_id_param.get("value") == "user_456"


@pytest.mark.asyncio
async def test_get_agent_messages_includes_user_id_clause():
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock",
        database_name="mockdb",
        container_name="mockcontainer",
        user_id="user_789",
    )
    client._initialized = True

    captured_query = None
    captured_params = None

    async def mock_query_items(query, parameters, model_class):
        nonlocal captured_query, captured_params
        captured_query = query
        captured_params = parameters
        return []

    client.query_items = mock_query_items

    await client.get_agent_messages("plan_xyz")

    assert captured_query is not None
    assert "c.user_id=@user_id" in captured_query
    user_id_param = next((p for p in captured_params if p.get("name") == "@user_id"), None)
    assert user_id_param is not None
    assert user_id_param.get("value") == "user_789"
