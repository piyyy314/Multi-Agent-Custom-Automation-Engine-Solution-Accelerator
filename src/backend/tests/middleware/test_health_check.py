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


def test_health_check_valid_password():
    """Test the health check endpoint with the correct password returns JSON details."""
    client = TestClient(app)
    response = client.get("/healthz?code=test123")

    assert response.status_code == 503
    json_data = response.json()
    assert "status" in json_data
    assert "results" in json_data


def test_health_check_empty_password_config():
    """Test that configuring an empty password does not leak JSON details when code is empty."""
    empty_app = FastAPI()
    empty_app.add_middleware(HealthCheckMiddleware, checks=checks, password="")
    client = TestClient(empty_app)

    # Passing ?code= should not expose JSON when password is empty
    response = client.get("/healthz?code=")
    assert response.status_code == 503
    assert response.text == "Service Unavailable"


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
