import os
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure src/App and src/backend are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../App")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import frontend_server


@pytest.fixture
def client(tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    index_file = build_dir / "index.html"
    index_file.write_text("<html>Index</html>")

    sample_asset = build_dir / "sample.txt"
    sample_asset.write_text("Sample Content")

    assets_dir = build_dir / "assets"
    assets_dir.mkdir()
    css_file = assets_dir / "style.css"
    css_file.write_text("body {}")

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("SENSITIVE DATA")

    orig_build_dir = frontend_server.BUILD_DIR
    orig_index_html = frontend_server.INDEX_HTML

    frontend_server.BUILD_DIR = str(build_dir)
    frontend_server.INDEX_HTML = str(index_file)

    test_client = TestClient(frontend_server.app)

    yield test_client

    frontend_server.BUILD_DIR = orig_build_dir
    frontend_server.INDEX_HTML = orig_index_html


def test_serve_valid_file(client):
    response = client.get("/sample.txt")
    assert response.status_code == 200
    assert response.text == "Sample Content"


def test_serve_nonexistent_route_returns_index(client):
    response = client.get("/some/spa/route")
    assert response.status_code == 200
    assert response.text == "<html>Index</html>"


def test_path_traversal_dot_dot_slash_prevented(client):
    response = client.get("/../secret.txt")
    assert response.status_code == 200
    assert response.text == "<html>Index</html>"
    assert "SENSITIVE DATA" not in response.text


def test_path_traversal_backslash_prevented(client):
    response = client.get("/..\\secret.txt")
    assert response.status_code == 200
    assert response.text == "<html>Index</html>"
    assert "SENSITIVE DATA" not in response.text
