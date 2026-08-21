import os
import sys
from unittest import mock

from starlette.middleware.cors import CORSMiddleware


def _clean_mocked_sys_modules():
    """Clean up sys.modules if other test files set global Mocks on real packages."""
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith(("pydantic", "fastapi", "starlette")) and isinstance(sys.modules[mod_name], mock.Mock):
            sys.modules.pop(mod_name, None)


def get_cors_origins(app):
    """Helper function to extract allow_origins from FastAPI middleware stack."""
    for middleware in app.user_middleware:
        if getattr(middleware, "cls", None) == CORSMiddleware:
            return middleware.kwargs.get("allow_origins", [])
    return []


def test_frontend_server_cors_dev_default():
    """Test that frontend_server configures local origins in default dev environment."""
    _clean_mocked_sys_modules()
    with mock.patch.dict(os.environ, {"APP_ENV": "dev", "ALLOWED_ORIGINS": "", "FRONTEND_SITE_NAME": ""}, clear=False):
        sys.modules.pop("frontend_server", None)
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../App")))
        try:
            import frontend_server
            origins = get_cors_origins(frontend_server.app)
            assert "*" not in origins
            assert "http://localhost:3000" in origins
            assert "http://127.0.0.1:3000" in origins
        finally:
            sys.modules.pop("frontend_server", None)


def test_frontend_server_cors_allowed_origins_env():
    """Test that frontend_server uses ALLOWED_ORIGINS environment variable when provided."""
    _clean_mocked_sys_modules()
    env = {
        "APP_ENV": "prod",
        "ALLOWED_ORIGINS": "https://myapp.contoso.com, https://admin.contoso.com",
        "FRONTEND_SITE_NAME": "",
    }
    with mock.patch.dict(os.environ, env, clear=False):
        sys.modules.pop("frontend_server", None)
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../App")))
        try:
            import frontend_server
            origins = get_cors_origins(frontend_server.app)
            assert "*" not in origins
            assert "https://myapp.contoso.com" in origins
            assert "https://admin.contoso.com" in origins
        finally:
            sys.modules.pop("frontend_server", None)
