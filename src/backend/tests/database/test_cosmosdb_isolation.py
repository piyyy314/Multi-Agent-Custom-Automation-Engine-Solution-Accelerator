"""Unit tests verifying CosmosDB user isolation scoping."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from common.database.cosmosdb import CosmosDBClient


@pytest.mark.asyncio
async def test_cosmosdb_get_plan_by_plan_id_user_scoping():
    """Verify get_plan_by_plan_id includes c.user_id=@user_id in query and parameters."""
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock-credential",
        database_name="mock_db",
        container_name="mock_container",
        user_id="user-123",
    )
    client._initialized = True
    client.query_items = AsyncMock(return_value=[])

    await client.get_plan_by_plan_id("plan-456")

    client.query_items.assert_called_once()
    query, parameters, _ = client.query_items.call_args[0]
    assert "c.user_id=@user_id" in query
    user_param = next((p for p in parameters if p["name"] == "@user_id"), None)
    assert user_param is not None
    assert user_param["value"] == "user-123"


@pytest.mark.asyncio
async def test_cosmosdb_delete_plan_by_plan_id_user_scoping():
    """Verify delete_plan_by_plan_id includes c.user_id=@user_id in query and parameters."""
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock-credential",
        database_name="mock_db",
        container_name="mock_container",
        user_id="user-123",
    )
    client._initialized = True
    mock_container = MagicMock()

    async def async_generator():
        if False:
            yield

    mock_container.query_items.return_value = async_generator()
    client.container = mock_container

    await client.delete_plan_by_plan_id("plan-456")

    mock_container.query_items.assert_called_once()
    kwargs = mock_container.query_items.call_args[1]
    query = kwargs["query"]
    params = kwargs["parameters"]
    assert "c.user_id=@user_id" in query
    user_param = next((p for p in params if p["name"] == "@user_id"), None)
    assert user_param is not None
    assert user_param["value"] == "user-123"


@pytest.mark.asyncio
async def test_cosmosdb_get_mplan_user_scoping():
    """Verify get_mplan includes c.user_id=@user_id in query and parameters."""
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock-credential",
        database_name="mock_db",
        container_name="mock_container",
        user_id="user-123",
    )
    client._initialized = True
    client.query_items = AsyncMock(return_value=[])

    await client.get_mplan("plan-456")

    client.query_items.assert_called_once()
    query, parameters, _ = client.query_items.call_args[0]
    assert "c.user_id=@user_id" in query
    user_param = next((p for p in parameters if p["name"] == "@user_id"), None)
    assert user_param is not None
    assert user_param["value"] == "user-123"


@pytest.mark.asyncio
async def test_cosmosdb_get_agent_messages_user_scoping():
    """Verify get_agent_messages includes c.user_id=@user_id in query and parameters."""
    client = CosmosDBClient(
        endpoint="https://mock.documents.azure.com:443/",
        credential="mock-credential",
        database_name="mock_db",
        container_name="mock_container",
        user_id="user-123",
    )
    client._initialized = True
    client.query_items = AsyncMock(return_value=[])

    await client.get_agent_messages("plan-456")

    client.query_items.assert_called_once()
    query, parameters, _ = client.query_items.call_args[0]
    assert "c.user_id=@user_id" in query
    user_param = next((p for p in parameters if p["name"] == "@user_id"), None)
    assert user_param is not None
    assert user_param["value"] == "user-123"
