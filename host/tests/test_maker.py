from __future__ import annotations

import hashlib
import hmac
import json
import re
import subprocess
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mazhost.buddy import Buddy
from mazhost.config import Settings
from mazhost.maker import EnderForgeSource, FakePrinterSource, Maker, OctoPrintSource, install_maker_routes


@pytest.fixture
def signed_decide(monkeypatch):
    key = "maker-test-device-key"
    monkeypatch.setenv("PIBLO_ASK_DEVICE_KEY", key)
    monkeypatch.delenv("PIBLO_ASK_LEGACY_DEVICE_DECIDE", raising=False)
    monkeypatch.delenv("MAZ_ASK_LEGACY_DEVICE_DECIDE", raising=False)

    def decide(buddy, rid, decision="allow"):
        item = next(item for item in buddy.pending() if item["id"] == rid)
        message = f"{rid}:{item['digest']}:{decision}:{item['nonce']}".encode()
        proof = hmac.new(key.encode(), message, hashlib.sha256).hexdigest()
        return buddy.decide(rid, decision, proof=proof)

    return decide


def job(state="Printing", completion=42, name="bracket", elapsed=100):
    return {"state": state, "job": {"file": {"name": name, "path": name, "origin": "local", "date": 1}},
            "progress": {"completion": completion, "printTimeLeft": 1080, "printTime": elapsed}}


def octo(tmp_path, state="Printing"):
    key = tmp_path / "key"
    key.write_text("secret-key")
    sent = []
    current = job(state)

    def handler(request):
        assert request.headers["X-Api-Key"] == "secret-key"
        if request.method == "POST":
            assert request.url.path == "/api/job"
            sent.append(json.loads(request.content))
            return httpx.Response(204)
        if request.url.path == "/api/job":
            return httpx.Response(200, json=current)
        assert request.url.path == "/api/printer"
        return httpx.Response(200, json={"state": {"text": current["state"]},
                             "temperature": {"tool0": {"actual": 210, "target": 210}}})

    source = OctoPrintSource("http://printer.test", str(key), httpx.Client(transport=httpx.MockTransport(handler)))
    return source, sent, current


@pytest.mark.parametrize("state,expected", [("Printing", "Printing: bracket, 42%, about 18 min left"),
    ("Operational", "Printer idle"), ("Heating", "Printer heating"),
    ("Offline", "Can't reach the printer"), ("Error", "Printer error")])
def test_status_words(tmp_path, state, expected):
    source, _, _ = octo(tmp_path, state)
    view = Maker(source, Buddy()).printer()
    assert view["text"] == expected
    assert view["nozzle_text"] == "Nozzle 210 of 210 °C"
    assert view["raw"]["job"] == "bracket"


def test_enderforge_contract_and_not_ready(monkeypatch):
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        assert kwargs["timeout"] and kwargs["stdin"] == subprocess.DEVNULL
        if args[-2] == "next":
            return subprocess.CompletedProcess(args, 0, json.dumps({"next": {"step": "C1", "title": "Look over the printer", "you": "answer 9 quick questions at the printer"}}), "")
        return subprocess.CompletedProcess(args, 0, json.dumps({"connection": "Printing", "job": "bracket", "progress": 42, "nozzle": {"actual": 210, "target": 210}}), "")
    monkeypatch.setattr(subprocess, "run", run)
    source = EnderForgeSource("ef")
    assert Maker(source, Buddy()).printer()["text"] == "Printing: bracket, 42%"
    assert "Look over the printer" in source.next_step()["text"]
    assert calls == [["ef", "status", "--json"], ["ef", "next", "--json"]]
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 3, "", "private diagnostics"))
    assert Maker(source, Buddy()).printer()["text"] == "Can't reach the printer"


@pytest.mark.parametrize("payload,code", [("not json", 0), ('{"connection": "Offline"}', 1), ('[]', 0)])
def test_enderforge_errors_are_plain_and_no_stderr_leaks(monkeypatch, payload, code):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, code, payload, "secret"))
    assert Maker(EnderForgeSource("ef"), Buddy()).printer()["state"] == "error"


@pytest.mark.parametrize("end,kind", [("finished", "finished"), ("error", "failed"), ("offline", "offline")])
def test_transition_alerts_once(end, kind):
    source = FakePrinterSource({"state": "printing", "job": "bracket", "progress": 42})
    buddy = Buddy()
    maker = Maker(source, buddy)
    assert maker.poll()["alerts"] == []
    source.value = {"state": end, "job": "bracket", "progress": 100 if end == "finished" else 42}
    assert maker.poll()["alerts"] == [kind]
    assert maker.poll()["alerts"] == []
    assert len(buddy._alerts) == 1


def test_idle_is_not_proof_of_success():
    source = FakePrinterSource({"state": "printing", "job": "bracket", "progress": 42})
    maker = Maker(source, Buddy())
    maker.poll()
    source.value = {"state": "idle", "job": "bracket", "progress": 42}
    assert maker.poll()["alerts"] == []


@pytest.mark.parametrize("action", ["pause", "cancel"])
@pytest.mark.parametrize("decision", ["allow", "deny", "cancel"])
def test_safe_actions_require_allow_and_are_not_replayed(tmp_path, action, decision, signed_decide):
    source, sent, _ = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(source, buddy, actions=source)
    request = maker.action(action)
    rid = request["id"]
    assert request["status"] == "pending" and sent == []
    pending = buddy.pending()[0]
    assert pending["category"] == "other" and "bracket" in pending["summary"]
    assert maker.action(action, rid)["status"] == "pending" and sent == []
    if decision == "allow":
        for proof in ("", "invalid"):
            with pytest.raises(PermissionError, match="device_proof_required"):
                buddy.decide(rid, "allow", proof=proof)
            assert maker.action(action, rid)["status"] == "pending" and sent == []
    signed_decide(buddy, rid, decision)
    result = maker.action(action, rid)
    assert result["status"] == ("sent" if decision == "allow" else "denied")
    expected = {"command": action, **({"action": "pause"} if action == "pause" else {})}
    assert sent == ([expected] if decision == "allow" else [])
    maker.action(action, rid)
    assert len(sent) == int(decision == "allow")


def test_wrong_action_unknown_request_and_changed_job_fail_closed(tmp_path, signed_decide):
    source, sent, current = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(source, buddy, actions=source)
    rid = maker.action("cancel")["id"]
    signed_decide(buddy, rid)
    with pytest.raises(ValueError):
        maker.action("pause", rid)
    with pytest.raises(ValueError):
        maker.action("cancel", "unknown")
    current["job"]["file"]["name"] = "different print"
    assert maker.action("cancel", rid)["status"] == "stale"
    assert not sent


def test_status_falls_back_and_poll_consumes_approval(tmp_path, signed_decide):
    source, sent, _ = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(FakePrinterSource({"state": "offline"}), buddy, actions=source)
    assert maker.printer()["state"] == "printing"
    rid = maker.action("pause")["id"]
    signed_decide(buddy, rid)
    maker.poll()
    assert sent == [{"command": "pause", "action": "pause"}]


@pytest.mark.parametrize("data", [{"connection": "Printing", "nozzle": "invalid"},
    {"connection": 123}, {"connection": "Printing", "job": {"invalid": True}}])
def test_malformed_enderforge_fields_fail_closed(monkeypatch, data):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, json.dumps(data), ""))
    assert Maker(EnderForgeSource("ef"), Buddy()).printer()["state"] == "error"


def test_expired_approval_cannot_send(tmp_path, signed_decide):
    source, sent, _ = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(source, buddy, actions=source)
    rid = maker.action("cancel")["id"]
    signed_decide(buddy, rid)
    buddy._items[rid]["deadline"] = 0
    assert maker.action("cancel", rid)["status"] == "denied"
    assert not sent


@pytest.mark.parametrize("revoke", ["expiry", "halt"])
def test_approval_revoked_during_status_check_cannot_send(tmp_path, monkeypatch, revoke, signed_decide):
    source, sent, _ = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(source, buddy, actions=source)
    rid = maker.action("cancel")["id"]
    signed_decide(buddy, rid)
    original = source.status
    def status():
        if revoke == "expiry":
            buddy._items[rid]["deadline"] = 0
        else:
            buddy.set_halt(True)
        return original()
    monkeypatch.setattr(source, "status", status)
    assert maker.action("cancel", rid)["status"] == "denied"
    assert not sent


def test_network_failure_after_send_is_never_retried(tmp_path, monkeypatch, signed_decide):
    source, sent, _ = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(source, buddy, actions=source)
    def uncertain(action):
        sent.append(action)
        raise httpx.ReadTimeout("unknown outcome")
    monkeypatch.setattr(source, "send", uncertain)
    rid = maker.action("cancel")["id"]
    signed_decide(buddy, rid)
    assert maker.action("cancel", rid)["status"] == "uncertain"
    assert maker.action("cancel", rid)["status"] == "uncertain"
    assert sent == ["cancel"]


def test_same_filename_new_print_and_unsafe_actions_are_rejected(tmp_path, signed_decide):
    source, sent, current = octo(tmp_path)
    buddy = Buddy()
    maker = Maker(source, buddy, actions=source)
    rid = maker.action("pause")["id"]
    signed_decide(buddy, rid)
    current["progress"]["printTime"] = 1
    assert maker.action("pause", rid)["status"] == "stale"
    for action in ("start", "connect", "home", "G28", "M104", "M140", "firmware"):
        with pytest.raises(ValueError):
            maker.action(action)
        with pytest.raises(ValueError):
            source.send(action)
    assert not sent


def test_maker_routes_with_simulated_printer(tmp_path, monkeypatch, signed_decide):
    cfg = Settings(maker_enderforge_cmd="ef", data_dir=str(tmp_path), _env_file=None)
    api = FastAPI()
    source, sent, _ = octo(tmp_path)
    buddy = Buddy()
    maker = install_maker_routes(api, cfg, buddy)
    maker.source = maker.actions = source
    client = TestClient(api)
    monkeypatch.setattr("shutil.which", lambda _: None)
    monkeypatch.setattr(EnderForgeSource, "next_step", lambda _: {"text": "Next: check the printer"})
    assert client.get("/maker/printer").json()["state"] == "printing"
    assert client.get("/maker/next").json()["text"].startswith("Next:")
    assert len(client.get("/maker/accessories").json()["accessories"]) == 3
    assert client.post("/maker/accessories/make", json={"text": "stand at 60 degrees"}).json()["format"] == "scad"
    assert client.post("/maker/accessories/make", json={"text": "dragon"}).status_code == 422
    assert client.post("/maker/accessories/make", json={"text": ""}).status_code == 422
    for action in ("pause", "cancel"):
        pending = client.post(f"/maker/{action}").json()
        assert pending["status"] == "pending"
        signed_decide(buddy, pending["id"])
        assert client.post(f"/maker/{action}", json={"request_id": pending["id"]}).json()["status"] == "sent"
    assert len(sent) == 2
    assert client.post("/maker/poll").status_code == 200


def test_route_surface_and_bearer_auth(tmp_path):
    from mazhost.app import create_app
    cfg = Settings(token="test-maker-token", maker_enderforge_cmd="ef", data_dir=str(tmp_path), buddy_db="off", _env_file=None)
    client = TestClient(create_app(cfg))
    for method, path in [("GET", "/maker/printer"), ("GET", "/maker/next"), ("POST", "/maker/pause"),
        ("POST", "/maker/cancel"), ("POST", "/maker/poll"), ("GET", "/maker/accessories"), ("POST", "/maker/accessories/make")]:
        assert client.request(method, path).status_code == 401
    source = Path(__import__("mazhost.maker", fromlist=["__file__"]).__file__).read_text()
    assert not re.search(r'G28|M104|M140|["\'](?:start|connect|home|firmware|gcode)["\']', source, re.I)
    api = FastAPI()
    install_maker_routes(api, Settings(_env_file=None), Buddy())
    assert TestClient(api).get("/maker/printer").status_code == 503
