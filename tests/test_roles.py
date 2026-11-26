"""Which code reaches what: the vehicle code every trainee gets must not reach notes, other vehicles or the scenarios."""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def codes(client):
    """An exercise with two vehicles, notes, a message and a running scenario for the first."""
    data = client.post("/api/leitstelle", json={"name": "Roles"}).json()
    admin, vehicle = data["admin_code"], data["vehicle_code"]
    for name in ("Car1", "Car2"):
        client.get(f"/api/poll/{vehicle}", params={"name": name})
    client.post(f"/api/leitstelle/{admin}/update_note", json={"target_name": "Car1", "note": "secret"})
    client.post(f"/api/leitstelle/{admin}/message", json={"target_name": "Car2", "message": "only Car2"})
    scenario = client.get(f"/api/leitstelle/{admin}/scenarios").json()["scenarios"][0]["name"]
    client.post(f"/api/leitstelle/{admin}/scenario/start", json={"target_name": "Car1", "scenario_name": scenario})
    return data


SUPERVISOR_ROUTES = (
    ("post", "message", {"target_name": "Car1", "message": "x"}),
    ("get", "chat_history?target_name=Car2", None),
    ("post", "update_note", {"target_name": "Car1", "note": "x"}),
    ("post", "scenario/update_state", {"target_name": "Car1", "state": {}}),
)

DISPATCH_ROUTES = (
    ("post", "clear_special", {"target_name": "Car1"}),
    ("post", "clear_kurzstatus", {"target_name": "Car1"}),
    ("post", "set_status", {"target_name": "Car1", "status": "3"}),
    ("post", "claim", {"target_name": "Car1", "sf_name": "x"}),
    ("post", "unclaim", {"target_name": "Car1"}),
    ("post", "channel", {"name": "Leitstelle", "channel": "1"}),
    ("get", "scenarios", None),
    ("post", "scenario/discard", {"target_name": "Car1"}),
    ("post", "scenario/next", {"target_name": "Car1"}),
)


def _call(client, method, code, route, body):
    url = f"/api/leitstelle/{code}/{route}"
    return client.get(url) if method == "get" else client.post(url, json=body)


@pytest.mark.parametrize(("method", "route", "body"), SUPERVISOR_ROUTES)
def test_the_vehicle_code_is_refused_on_notes_messages_and_checklists(client, codes, method, route, body):
    assert _call(client, method, codes["vehicle_code"], route, body).json()["status"] == "error"


@pytest.mark.parametrize(("method", "route", "body"), SUPERVISOR_ROUTES)
def test_dispatch_and_unit_leader_reach_notes_messages_and_checklists(client, codes, method, route, body):
    for code in (codes["admin_code"], codes["staffelfuehrer_code"]):
        assert _call(client, method, code, route, body).json()["status"] == "success", code


@pytest.mark.parametrize(("method", "route", "body"), DISPATCH_ROUTES)
def test_only_the_dispatch_code_reaches_dispatch_actions(client, codes, method, route, body):
    for code in (codes["vehicle_code"], codes["staffelfuehrer_code"]):
        assert _call(client, method, code, route, body).json()["status"] == "error", code


def test_a_vehicle_poll_shows_only_the_vehicle_itself(client, codes):
    data = client.get(f"/api/poll/{codes['vehicle_code']}", params={"name": "Car1"}).json()
    assert [car["name"] for car in data["connections"]] == ["Car1"]
    own = data["connections"][0]
    assert own["note"] == ""
    assert own["sf_note"] == ""
    assert own["active_scenario"] is None
    assert own["checklist_state"] is None
    assert data["messages"] == []
    assert set(data["notices"]) <= {"Car1"}


def test_a_vehicle_poll_carries_its_own_messages_only(client, codes):
    data = client.get(f"/api/poll/{codes['vehicle_code']}", params={"name": "Car2"}).json()
    assert [message["text"] for message in data["messages"]] == ["only Car2"]


def test_dispatch_still_sees_every_vehicle_with_notes_and_scenarios(client, codes):
    data = client.get(f"/api/poll/{codes['admin_code']}").json()
    car1 = next(car for car in data["connections"] if car["name"] == "Car1")
    assert {car["name"] for car in data["connections"]} >= {"Car1", "Car2"}
    assert car1["note"] == "secret"
    assert car1["active_scenario"]["generated_entries"]
