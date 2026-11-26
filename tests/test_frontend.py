"""Serving of the built frontend: prerendered pages, built files, the shell and the exercise pages."""

import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from frontend import mount_frontend  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture
def build(tmp_path: Path) -> Path:
    """A built frontend with the shell, two prerendered pages, `build.json` and one asset."""
    directory = tmp_path / "dist"
    (directory / "assets").mkdir(parents=True)
    (directory / "pages" / "hilfe").mkdir(parents=True)
    (directory / "index.html").write_text("<!doctype html><title>shell</title>")
    (directory / "pages" / "index.html").write_text("<!doctype html><title>landing</title>")
    (directory / "pages" / "hilfe" / "index.html").write_text("<!doctype html><title>help</title>")
    (directory / "build.json").write_text("{}")
    (directory / "favicon.svg").write_text("<svg/>")
    (directory / "assets" / "app.js").write_text("console.info(1)")
    (tmp_path / "secret.txt").write_text("secret")
    return directory


@pytest.fixture
def client(build: Path) -> TestClient:
    """A bare app that serves only the frontend."""
    frontend_app = FastAPI()
    mount_frontend(frontend_app, build)
    return TestClient(frontend_app)


@pytest.fixture
def server(build: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """The whole server, reading the frontend from the test build."""
    monkeypatch.setenv("FRONTEND_DIR", str(build))
    return TestClient(app)


def test_prerendered_pages_are_served_for_indexing(client):
    for path, title in (("/", "landing"), ("/hilfe", "help"), ("/hilfe/", "help")):
        response = client.get(path)
        assert f"<title>{title}</title>" in response.text, path
        assert "x-robots-tag" not in response.headers, path


def test_built_files_are_served(client):
    assert client.get("/assets/app.js").text == "console.info(1)"
    assert client.get("/favicon.svg").text == "<svg/>"


def test_build_json_is_never_cached(client):
    assert client.get("/build.json").headers["cache-control"] == "no-store"


def test_other_paths_get_the_shell_kept_out_of_search_engines(client):
    response = client.get("/unknown/path")
    assert "<title>shell</title>" in response.text
    assert response.headers["x-robots-tag"] == "noindex, nofollow"


def test_each_page_has_one_address_only(client):
    for path in ("/index.html", "/pages/index.html", "/pages/hilfe/index.html", "/./index.html", "/hilfe/../index.html"):
        response = client.get(path)
        assert "<title>shell</title>" in response.text, path
        assert response.headers["x-robots-tag"] == "noindex, nofollow", path


def test_paths_cannot_leave_the_build(client):
    response = client.get("/..%2Fsecret.txt")
    assert "secret" not in response.text
    assert "<title>shell</title>" in response.text


def test_a_missing_asset_is_a_404(client):
    assert client.get("/assets/old-build-1234.js").status_code == 404


def test_api_and_scenario_paths_are_never_html(client):
    for path in ("/api", "/api/unknown", "/static/unknown.json"):
        assert client.get(path).status_code == 404, path


def test_exercise_pages_get_the_shell_for_known_codes(server):
    codes = server.post("/api/leitstelle", json={"name": "Pages"}).json()
    for path in (
        f"/leitstelle/{codes['admin_code']}",
        f"/staffelfuehrer/{codes['staffelfuehrer_code']}",
        f"/status?code={codes['vehicle_code']}&name=LHF%201",
    ):
        response = server.get(path, follow_redirects=False)
        assert response.status_code == 200, path
        assert "<title>shell</title>" in response.text, path
        assert response.headers["x-robots-tag"] == "noindex, nofollow", path


def test_exercise_pages_send_unknown_codes_to_the_landing_page(server):
    for path in ("/leitstelle/NOPE", "/staffelfuehrer/NOPE", "/status?code=NOPE&name=x", "/status"):
        response = server.get(path, follow_redirects=False)
        assert response.status_code == 307, path
        assert response.headers["location"] == "/", path


def test_a_unit_leader_code_on_the_vehicle_page_opens_the_unit_leader_view(server):
    codes = server.post("/api/leitstelle", json={"name": "Pages"}).json()
    response = server.get(f"/status?code={codes['staffelfuehrer_code']}&name=x", follow_redirects=False)
    assert response.headers["location"] == f"/staffelfuehrer/{codes['staffelfuehrer_code']}"

