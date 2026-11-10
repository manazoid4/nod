"""Device pairing (docs/protocol/DEVICE-PAIRING.md): code + Allow, UDP discovery."""
from __future__ import annotations

import socket
import time

import pytest
from fastapi.testclient import TestClient

from mazhost import pairing as pairing_mod
from mazhost.app import create_app
from mazhost.config import Settings
from mazhost.discovery import DISCOVER_LINE, DiscoveryResponder

TOKEN = "test-token-that-is-not-default"
H = {"Authorization": f"Bearer {TOKEN}"}
LAN = ("192.168.1.50", 50000)


def _as_ip(app):
    """This Starlette's TestClient can't set the peer; take it from X-Test-Ip instead."""
    async def wrapped(scope, receive, send):
        if scope["type"] == "http":
            hdrs = dict(scope["headers"])
            ip = hdrs.get(b"x-test-ip", LAN[0].encode()).decode()
            scope = {**scope, "client": (ip, 50000)}
        await app(scope, receive, send)
    return wrapped


def at(c, ip):
    """A client for the same app that appears to come from `ip`."""
    return TestClient(c.app, headers={"X-Test-Ip": ip})


def api():
    return TestClient(_as_ip(create_app(Settings(token=TOKEN, _env_file=None))))


def ask(c, device_id="piblo-0001", name="Piblo"):
    return c.post("/pair/device/request", json={"device_id": device_id, "name": name})


def test_happy_path_token_exactly_once():
    c = api()
    r = ask(c)
    assert r.status_code == 200
    d = r.json()
    assert len(d["code"]) == 6 and d["code"].isdigit() and len(d["request_id"]) >= 22
    assert d["expires_in_seconds"] == 120
    rid = d["request_id"]
    assert c.get(f"/pair/device/request/{rid}").json() == {"status": "pending"}
    pend = c.get("/pair/device/pending", headers=H).json()["requests"]
    assert len(pend) == 1
    assert pend[0]["request_id"] == rid and pend[0]["code"] == d["code"]
    assert pend[0]["name"] == "Piblo" and pend[0]["device_id"] == "piblo-0001"
    assert pend[0]["ip"] == LAN[0] and pend[0]["age_s"] >= 0
    # Not approved yet: no token anywhere.
    assert TOKEN not in c.get(f"/pair/device/request/{rid}").text
    assert c.post(f"/pair/device/{rid}/approve", headers=H).json() == {"ok": True}
    assert c.get("/pair/device/pending", headers=H).json() == {"requests": []}
    got = c.get(f"/pair/device/request/{rid}").json()
    assert got == {"status": "approved", "token": TOKEN, "port": 8787}
    assert c.get(f"/pair/device/request/{rid}").status_code == 404
    assert c.post(f"/pair/device/{rid}/approve", headers=H).status_code == 404


def test_deny_is_terminal_then_404():
    c = api()
    rid = ask(c).json()["request_id"]
    assert c.post(f"/pair/device/{rid}/deny", headers=H).json() == {"ok": True}
    r = c.get(f"/pair/device/request/{rid}")
    assert r.json() == {"status": "denied"} and TOKEN not in r.text
    assert c.get(f"/pair/device/request/{rid}").status_code == 404
    assert c.post(f"/pair/device/{rid}/approve", headers=H).status_code == 404


def test_expiry(monkeypatch):
    c = api()
    rid = ask(c).json()["request_id"]
    real = time.monotonic()
    monkeypatch.setattr(pairing_mod.time, "monotonic", lambda: real + 121)
    assert c.get("/pair/device/pending", headers=H).json() == {"requests": []}
    assert c.post(f"/pair/device/{rid}/approve", headers=H).status_code == 404
    assert c.get(f"/pair/device/request/{rid}").json() == {"status": "expired"}
    assert c.get(f"/pair/device/request/{rid}").status_code == 404


def test_approved_but_uncollected_expires_without_token(monkeypatch):
    c = api()
    rid = ask(c).json()["request_id"]
    c.post(f"/pair/device/{rid}/approve", headers=H)
    real = time.monotonic()
    monkeypatch.setattr(pairing_mod.time, "monotonic", lambda: real + 200)
    r = c.get(f"/pair/device/request/{rid}")
    assert r.json() == {"status": "expired"} and TOKEN not in r.text


def test_other_ip_gets_404_and_cannot_steal_token():
    c = api()
    rid = ask(c).json()["request_id"]
    c.post(f"/pair/device/{rid}/approve", headers=H)
    thief = at(c, "192.168.1.99")
    assert thief.get(f"/pair/device/request/{rid}").status_code == 404
    assert thief.get("/pair/device/request/does-not-exist").status_code == 404
    # The thief's probe did not consume it.
    assert c.get(f"/pair/device/request/{rid}").json()["status"] == "approved"


def test_same_device_id_replaces_older_request():
    c = api()
    old = ask(c).json()["request_id"]
    new = ask(c).json()["request_id"]
    assert old != new
    assert c.get(f"/pair/device/request/{old}").status_code == 404
    assert [p["request_id"] for p in c.get("/pair/device/pending", headers=H).json()["requests"]] == [new]


def test_max_four_pending_then_429_replace_still_ok():
    c = api()
    for i in range(4):
        # Different IPs so the per-IP limit is not what trips.
        cli = at(c, f"192.168.1.{10 + i}")
        assert ask(cli, device_id=f"dev-{i:04d}").status_code == 200
    extra = at(c, "192.168.1.80")
    r = ask(extra, device_id="dev-9999")
    assert r.status_code == 429 and r.json()["detail"] == "too_many_requests"
    # Replacing an existing device's request does not add a pending one.
    same = at(c, "192.168.1.10")
    assert ask(same, device_id="dev-0000").status_code == 200
    assert len(c.get("/pair/device/pending", headers=H).json()["requests"]) == 4
    # Oldest first.
    ages = [p["age_s"] for p in c.get("/pair/device/pending", headers=H).json()["requests"]]
    assert ages == sorted(ages, reverse=True)


def test_per_ip_six_a_minute_then_429(monkeypatch):
    c = api()
    for i in range(6):
        assert ask(c, device_id=f"dev-{i:04d}").status_code == 200
        c.post(f"/pair/device/{c.get('/pair/device/pending', headers=H).json()['requests'][-1]['request_id']}/deny", headers=H)
    assert ask(c, device_id="dev-0007").status_code == 429
    real = time.monotonic()
    monkeypatch.setattr(pairing_mod.time, "monotonic", lambda: real + 61)
    assert ask(c, device_id="dev-0007").status_code == 200


@pytest.mark.parametrize("body", [
    {}, {"device_id": "abc", "name": "x"}, {"device_id": "x" * 33, "name": "x"},
    {"device_id": "bad id!", "name": "x"}, {"device_id": "good-id", "name": ""},
    {"device_id": "good-id", "name": "x" * 25}, {"device_id": "good-id", "name": "café"},
    {"device_id": "good-id", "name": "a\nb"}, {"device_id": 1234, "name": "x"},
    {"device_id": "good-id"}, [], "str",
])
def test_bad_bodies_are_400(body):
    assert api().post("/pair/device/request", json=body).status_code == 400


def test_non_json_body_is_400():
    assert api().post("/pair/device/request", content=b"nope").status_code == 400


def test_bearer_required_on_pending_approve_deny():
    c = api()
    rid = ask(c).json()["request_id"]
    bad = {"Authorization": "Bearer nope"}
    for hdrs in ({}, bad):
        assert c.get("/pair/device/pending", headers=hdrs).status_code == 401
        assert c.post(f"/pair/device/{rid}/approve", headers=hdrs).status_code == 401
        assert c.post(f"/pair/device/{rid}/deny", headers=hdrs).status_code == 401
    # Still pending, still no token.
    assert c.get(f"/pair/device/request/{rid}").json() == {"status": "pending"}


def test_unknown_id_approve_deny_404():
    c = api()
    assert c.post("/pair/device/nope/approve", headers=H).status_code == 404
    assert c.post("/pair/device/nope/deny", headers=H).status_code == 404


def test_pairing_never_touches_buddy_approvals():
    c = api()
    before = c.get("/buddy/events", headers=H).json()
    rid = ask(c).json()["request_id"]
    c.post(f"/pair/device/{rid}/approve", headers=H)
    c.get(f"/pair/device/request/{rid}")
    assert c.get("/buddy/events", headers=H).json() == before


def _free_udp_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_udp_responder_replies_to_exact_line_only():
    import json

    r = DiscoveryResponder(_free_udp_port(), 8787)
    r.start()
    try:
        assert r.bound_port
        cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cli.settimeout(1.0)
        for junk in (b"PIBLO-DISCOVER 2\n", b"PIBLO-DISCOVER 1", b"hello", DISCOVER_LINE + b"x"):
            cli.sendto(junk, ("127.0.0.1", r.bound_port))
        with pytest.raises(socket.timeout):
            cli.recvfrom(512)
        cli.sendto(DISCOVER_LINE, ("127.0.0.1", r.bound_port))
        data, _ = cli.recvfrom(512)
        assert data.endswith(b"\n")
        msg = json.loads(data)
        assert msg["piblo"] == 1 and msg["port"] == 8787
        assert 0 < len(msg["name"]) <= 32 and msg["version"]
        assert TOKEN not in data.decode()
        cli.close()
    finally:
        r.stop()


def test_udp_disabled_and_port_in_use_do_not_crash():
    off = DiscoveryResponder(0, 8787)
    off.start()
    assert off.bound_port == 0
    busy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    busy.bind(("0.0.0.0", 0))
    clash = DiscoveryResponder(busy.getsockname()[1], 8787)
    clash.start()  # logs and carries on
    assert clash.bound_port == 0
    clash.stop()
    busy.close()
