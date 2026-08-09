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


class MockCheck:
    """Mock health check compatible with the middleware's strict __await__ check."""
    def __init__(self, status=True, message="Success"):
        self.status = status
        self.message = message

    def __await__(self):
        async def _run():
            return HealthCheckResult(self.status, self.message)
        return _run().__await__()

    def __call__(self):
        return self


def test_health_check_empty_password_rejection():
    """Test that empty or blank passwords are rejected and do not expose detailed JSON."""
    for empty_pw in ("", "   ", None):
        test_app = FastAPI()

        test_app.add_middleware(
            HealthCheckMiddleware,
            checks={"success": MockCheck(status=True, message="Success")},
            password=empty_pw
        )

        test_client = TestClient(test_app)

        # Omitted code
        response = test_client.get("/healthz")
        assert response.status_code == 200
        assert response.text == "OK"

        # code is empty string (if query param code= is supplied)
        response_with_code = test_client.get("/healthz?code=")
        assert response_with_code.status_code == 200
        assert response_with_code.text == "OK"  # Must be plain text "OK", not detailed JSON!

        # code is spaces (if code=   is supplied)
        response_with_spaces = test_client.get("/healthz?code=   ")
        assert response_with_spaces.status_code == 200
        assert response_with_spaces.text == "OK"  # Must be plain text "OK", not detailed JSON!


def test_health_check_valid_password_exposure():
    """Test that a valid password exposes the detailed JSON only when the correct password is provided."""
    test_app = FastAPI()

    test_app.add_middleware(
        HealthCheckMiddleware,
        checks={"custom_check": MockCheck(status=True, message="Specific detailed message")},
        password="secure_token_123"
    )

    test_client = TestClient(test_app)

    # Correct password
    response = test_client.get("/healthz?code=secure_token_123")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["results"]["custom_check"]["message"] == "Specific detailed message"

    # Incorrect password
    response_wrong = test_client.get("/healthz?code=wrong_token")
    assert response_wrong.status_code == 200
    assert response_wrong.text == "OK"  # Plain text, not JSON

    # Missing password
    response_missing = test_client.get("/healthz")
    assert response_missing.status_code == 200
    assert response_missing.text == "OK"  # Plain text, not JSON


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
