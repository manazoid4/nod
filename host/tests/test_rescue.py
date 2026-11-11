"""Rescue persists locally, rejects oversized updates, and fits the device buffer."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mazhost.config import Settings
from mazhost.security import Security


def client_for(data_dir):
    from mazhost.rescue import install_rescue_routes

    api = FastAPI()
    security = Security(Settings(token="rescue-test-placeholder", _env_file=None))
    install_rescue_routes(api, security.authorize, data_dir)
    return TestClient(api, headers={"Authorization": "Bearer rescue-test-placeholder"})


def test_round_trip_survives_new_app(tmp_path):
    client = client_for(tmp_path)
    assert client.get("/rescue").json() == {
        "contacts": [], "travel": "", "notes": "", "emergency_instructions": "",
    }
    payload = {
        "contacts": [{"name": "Alex", "phone": "+00 000 000"}],
        "travel": "Return train: platform 4",
        "notes": "Spare key with Alex",
        "emergency_instructions": "Contact Alex if help is needed",
    }
    assert client.put("/rescue", json=payload).json() == payload
    assert client_for(tmp_path).get("/rescue").json() == payload
    assert json.loads((tmp_path / "rescue.json").read_text(encoding="utf-8")) == payload
    compact = client.get("/rescue/compact")
    assert compact.headers["content-type"].startswith("text/plain")
    assert compact.text.splitlines() == [
        "Alex: +00 000 000", "Emergency: Contact Alex if help is needed",
        "Travel: Return train: platform 4", "Notes: Spare key with Alex",
    ]


@pytest.mark.parametrize("bad", [
    {"notes": "x" * 8193},
    {"notes": "\U0001f642" * 4096},
    {"contacts": [{"name": "Alex", "phone": "+00"}] * 9},
    {"contacts": [{"name": "", "phone": "+00"}]},
    {"contacts": [{"name": "Alex", "phone": "a\nnew line"}]},
    {"notes": 123},
    {"unknown": "discarding fields would hide mistakes"},
])
def test_invalid_update_preserves_saved_data(tmp_path, bad):
    client = client_for(tmp_path)
    good = client.put("/rescue", json={"notes": "keep this"}).json()
    response = client.put("/rescue", json=bad)
    assert response.status_code == 422
    assert client.get("/rescue").json() == good


def test_compact_unicode_budget_keeps_contacts_first(tmp_path):
    client = client_for(tmp_path)
    contacts = [{"name": "\u5bb6" * 64, "phone": f"+00 000 {n:03d}"} for n in range(8)]
    response = client.put("/rescue", json={
        "contacts": contacts, "travel": "\u65c5" * 800,
        "notes": "\U0001f642" * 800, "emergency_instructions": "Get help " * 100,
    })
    assert response.status_code == 200
    compact = client.get("/rescue/compact")
    assert 0 < len(compact.content) <= 2048
    assert "\ufffd" not in compact.text
    lines = compact.text.splitlines()
    assert all(len(line.encode("utf-8")) <= 96 for line in lines)
    for n, contact in enumerate(contacts):
        assert contact["phone"] in lines[n]
    assert lines[8].startswith("Emergency:")


@pytest.mark.parametrize("method,path", [("get", "/rescue"), ("put", "/rescue"), ("get", "/rescue/compact")])
@pytest.mark.parametrize("authorization", [None, "Bearer wrong-placeholder"])
def test_all_routes_require_existing_bearer_auth(tmp_path, method, path, authorization):
    client = client_for(tmp_path)
    client.headers.pop("Authorization")
    headers = {"Authorization": authorization} if authorization else {}
    response = getattr(client, method)(path, headers=headers, **({"json": {}} if method == "put" else {}))
    assert response.status_code == 401
    assert not (tmp_path / "rescue.json").exists()


def test_corrupt_store_reports_error_without_overwriting(tmp_path):
    (tmp_path / "rescue.json").write_text("not json", encoding="utf-8")
    response = client_for(tmp_path).get("/rescue")
    assert response.status_code == 503
    assert response.json() == {"detail": "rescue_data_invalid"}
    assert (tmp_path / "rescue.json").read_text(encoding="utf-8") == "not json"
