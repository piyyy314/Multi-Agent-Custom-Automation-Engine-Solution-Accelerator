from asyncio import sleep

from fastapi import FastAPI
from starlette.testclient import TestClient

from src.backend.middleware.health_check import HealthCheckMiddleware, HealthCheckResult


# Updated helper functions for test health checks
async def successful_check():
    """Simulates a successful check."""
    await sleep(0.1)  # Simulate async operation
    return HealthCheckResult(status=True, message="Successful check")


async def failing_check():
    """Simulates a failing check."""
    await sleep(0.1)  # Simulate async operation
    return HealthCheckResult(status=False, message="Failing check")


# Test application setup
app = FastAPI()

checks = {
    "success": successful_check,
    "failure": failing_check,
}

app.add_middleware(HealthCheckMiddleware, checks=checks, password="test123")


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


def test_health_check_success():
    """Test the health check endpoint with successful checks."""
    client = TestClient(app)
    response = client.get("/healthz")

    assert response.status_code == 503  # Because one check is failing
    assert response.text == "Service Unavailable"


def test_health_check_correct_password():
    """Test the health check endpoint with a correct password."""
    app_success = FastAPI()
    app_success.add_middleware(
        HealthCheckMiddleware,
        checks={"success": successful_check},
        password="test123",
    )
    client = TestClient(app_success)
    response = client.get("/healthz?code=test123")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] is True
    assert "Default" in json_data["results"]


def test_health_check_empty_password_bypass_prevention():
    """Test that empty string or None password prevents auth bypass via ?code=."""
    app_empty = FastAPI()
    app_empty.add_middleware(
        HealthCheckMiddleware,
        checks={"success": successful_check},
        password="",
    )
    client = TestClient(app_empty)

    # Calling with empty code parameter
    response_empty_code = client.get("/healthz?code=")
    assert response_empty_code.status_code == 200
    assert response_empty_code.text == "OK"

    # Calling with non-empty code parameter
    response_some_code = client.get("/healthz?code=anything")
    assert response_some_code.status_code == 200
    assert response_some_code.text == "OK"


def test_root_endpoint():
    """Test the root endpoint to ensure the app is functioning."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_health_check_missing_password():
    """Test the health check endpoint without a password."""
    client = TestClient(app)
    response = client.get("/healthz")

    assert response.status_code == 503  # Unauthorized access without correct password
    assert response.text == "Service Unavailable"


def test_health_check_incorrect_password():
    """Test the health check endpoint with an incorrect password."""
    client = TestClient(app)
    response = client.get("/healthz?code=wrongpassword")

    assert response.status_code == 503  # Because one check is failing
    assert response.text == "Service Unavailable"
