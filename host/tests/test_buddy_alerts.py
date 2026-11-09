"""Generic alerts: webhook / reminder intake, ack+snooze outcomes, approval routing."""
from __future__ import annotations

from fastapi.testclient import TestClient

from mazhost import buddy as buddy_mod
from mazhost.app import create_app
from mazhost.config import Settings

TOKEN = "test-token-that-is-not-default"
H = {"Authorization": f"Bearer {TOKEN}"}
ALERT = {"source": "ci", "kind": "sla", "title": "SLA breach: ticket #123", "priority": "urgent",
         "actions": ["ack", "snooze"]}


def api():
    return TestClient(create_app(Settings(token=TOKEN, _env_file=None)))


def test_alert_requires_token_and_validates():
    c = api()
    assert c.post("/buddy/alert", json=ALERT).status_code == 401
    assert c.post("/buddy/alert", json=ALERT, headers={"Authorization": "Bearer nope"}).status_code == 401
    assert c.get("/buddy/alerts").status_code == 401
    for bad in ({**ALERT, "title": ""}, {**ALERT, "title": "x" * 61}, {**ALERT, "body": "x" * 201},
                {**ALERT, "priority": "panic"}, {**ALERT, "kind": "nope"}, {**ALERT, "actions": ["delete"]}):
        assert c.post("/buddy/alert", json=bad, headers=H).status_code == 422
    # approve/reject belong to the approval path only
    assert c.post("/buddy/alert", json={**ALERT, "actions": ["approve"]}, headers=H).status_code == 400


def test_alert_lands_in_ring_with_schema():
    c = api()
    aid = c.post("/buddy/alert", json=ALERT, headers=H).json()["id"]
    ev = c.get("/buddy/events", headers=H).json()["events"][-1]
    assert ev["kind"] == "alert" and ev["alert"]["id"] == aid
    assert {"source", "kind", "title", "body", "priority", "actions", "created_at"} <= set(ev["alert"])
    assert "outcome" not in ev["alert"]
    for i in range(buddy_mod.MAX_EVENTS + 5):
        c.post("/buddy/alert", json={**ALERT, "title": f"n{i}"}, headers=H)
    ids, since = [], 0
    while True:  # the poll is paged, so walk it
        page = c.get(f"/buddy/events?since={since}", headers=H).json()
        if not page["events"]:
            break
        ids += [e["id"] for e in page["events"]]
        since = page["last"]
    assert len(ids) == buddy_mod.MAX_EVENTS


def test_alert_ack_and_snooze_store_outcome(monkeypatch):
    c = api()
    aid = c.post("/buddy/alert", json=ALERT, headers=H).json()["id"]
    assert c.post(f"/buddy/alert/{aid}/snooze", json={"minutes": 5}, headers=H).json()["outcome"] == "snoozed"
    n = c.get("/buddy/events", headers=H).json()["last"]
    assert c.get("/buddy/events", headers=H).json()["last"] == n  # still snoozed: no re-fire
    real = buddy_mod.time.time
    monkeypatch.setattr(buddy_mod.time, "time", lambda: real() + 301)
    assert c.get("/buddy/events", headers=H).json()["last"] == n + 1  # nags again
    assert c.post(f"/buddy/alert/{aid}/ack", headers=H).json()["outcome"] == "acked"
    monkeypatch.setattr(buddy_mod.time, "time", lambda: real() + 99999)
    assert c.get("/buddy/events", headers=H).json()["last"] == n + 1  # acked: silent for good
    stored = [a for a in c.get("/buddy/alerts", headers=H).json()["alerts"] if a["id"] == aid][0]
    assert stored["outcome"] == "acked"
    assert c.post("/buddy/alert/al-nope/ack", headers=H).status_code == 404


def test_alert_action_must_be_offered():
    c = api()
    aid = c.post("/buddy/alert", json={**ALERT, "actions": ["ack"]}, headers=H).json()["id"]
    assert c.post(f"/buddy/alert/{aid}/snooze", headers=H).status_code == 400


def test_delayed_reminder_fires_when_due(monkeypatch):
    c = api()
    r = c.post("/buddy/alert", json={**ALERT, "kind": "reminder", "delay_seconds": 60}, headers=H).json()
    assert r["scheduled"] is True
    assert c.get("/buddy/events", headers=H).json()["events"] == []
    real = buddy_mod.time.time
    monkeypatch.setattr(buddy_mod.time, "time", lambda: real() + 61)
    assert c.get("/buddy/events", headers=H).json()["events"][0]["alert"]["id"] == r["id"]


def test_expired_alert_never_fires(monkeypatch):
    c = api()
    c.post("/buddy/alert", json={**ALERT, "delay_seconds": 30, "expires_in": 10}, headers=H)
    real = buddy_mod.time.time
    monkeypatch.setattr(buddy_mod.time, "time", lambda: real() + 100)
    assert c.get("/buddy/events", headers=H).json()["events"] == []


def test_events_poll_is_paged_to_fit_the_device_buffer():
    import json
    c = api()
    big = {**ALERT, "title": "t" * 60, "body": "é" * 200}
    for _ in range(buddy_mod.MAX_EVENTS):
        c.post("/buddy/alert", json=big, headers=H)
    seen, since = [], 0
    for _ in range(buddy_mod.MAX_EVENTS):
        r = c.get(f"/buddy/events?since={since}", headers=H)
        assert len(r.content) <= 6144
        body = r.json()
        if not body["events"]:
            break
        seen += [e["id"] for e in body["events"]]
        since = body["last"]
    assert seen == sorted(set(seen)) and len(seen) == buddy_mod.MAX_EVENTS
    assert json.dumps(c.get("/buddy/events?since=0", headers=H).json()["events"][0])


def test_full_alert_table_rejects_instead_of_evicting_pending():
    c = api()
    first = c.post("/buddy/alert", json={**ALERT, "delay_seconds": 600}, headers=H).json()["id"]
    ids = [c.post("/buddy/alert", json=ALERT, headers=H).json()["id"] for _ in range(buddy_mod.MAX_ALERTS - 1)]
    assert c.post("/buddy/alert", json=ALERT, headers=H).status_code == 429
    assert c.post("/buddy/alert", json={"kind": "approval", "title": "Bash"}, headers=H).status_code == 200  # approvals unaffected
    c.post(f"/buddy/alert/{ids[0]}/ack", headers=H)                      # answered alerts may be evicted
    assert c.post("/buddy/alert", json=ALERT, headers=H).status_code == 200
    kept = {a["id"] for a in c.get("/buddy/alerts", headers=H).json()["alerts"]}
    assert first in kept and ids[0] not in kept


def test_delayed_approval_is_rejected():
    c = api()
    assert c.post("/buddy/alert", json={"kind": "approval", "title": "Bash", "delay_seconds": 5}, headers=H).status_code == 400


def test_voice_reminder_command_schedules_an_alert():
    c = api()
    sid = c.post("/session/start", headers=H).json()["session_id"]
    r = c.post("/turn/text", json={"session_id": sid, "text": "remind me in 1 minute to stretch"}, headers=H)
    assert r.status_code == 200
    a = c.get("/buddy/alerts", headers=H).json()["alerts"][-1]
    assert a["kind"] == "reminder" and a["title"] == "stretch" and a["actions"] == ["ack", "snooze"]


def test_approval_kind_routes_through_existing_queue_and_halt():
    c = api()
    r = c.post("/buddy/alert", json={"kind": "approval", "title": "Bash", "body": "npm test",
                                     "source": "agent"}, headers=H).json()
    assert r["routed"] == "approval"
    assert c.get("/buddy/events", headers=H).json()["events"] == []  # never in the notify ring
    assert [p["id"] for p in c.get("/buddy/pending", headers=H).json()["pending"]] == [r["id"]]
    c.post("/buddy/halt", json={"on": True}, headers=H)  # Halt still fails closed
    assert c.get(f"/buddy/state?id={r['id']}", headers=H).json()["decision"] == "deny"
    r2 = c.post("/buddy/alert", json={"kind": "approval", "title": "Bash"}, headers=H).json()
    assert r2["decision"] == "deny"
    # the only way to approve is still /buddy/decide
    assert c.post("/buddy/decide", json={"id": r2["id"], "decision": "allow"}, headers=H).json()["decision"] == "deny"


# ---- The Nod: details + long-press flag + nod log ----
def _nod(c, **kw):
    body = {"kind": "approval", "title": "Pay Acme", "source": "bank", "nod": True, "amount": "£42.00",
            "recipient": "Acme Ltd", "category": "payment", **kw}
    return c.post("/buddy/alert", json=body, headers=H).json()


def test_nod_fields_reach_the_device_summary():
    c = api()
    r = _nod(c)
    item = c.get("/buddy/summary", headers=H).json()["items"][0]
    assert item["id"] == r["id"] and item["amount"] == "£42.00" and item["recipient"] == "Acme Ltd"
    assert item["category"] == "payment" and item["nod"] is True
    # the firmware reads one text field: head / amount / recipient on three lines
    assert item["summary"] == "THE NOD  PAYMENT" + chr(10) + "£42.00" + chr(10) + "to Acme Ltd"


def test_nod_fields_are_truncated_and_category_normalised():
    c = api()
    _nod(c, amount="£" + "9" * 40, recipient="R" * 90, category="Wire-Transfer")
    item = c.get("/buddy/summary", headers=H).json()["items"][0]
    assert len(item["amount"]) == 16 and len(item["recipient"]) == 40 and item["category"] == "other"
    _nod(c, category="DELETE")
    assert c.get("/buddy/summary", headers=H).json()["items"][1]["category"] == "delete"


def test_plain_approval_summary_is_unchanged():
    c = api()
    c.post("/buddy/alert", json={"kind": "approval", "title": "Bash", "body": "npm test"}, headers=H)
    item = c.get("/buddy/summary", headers=H).json()["items"][0]
    assert not {"amount", "recipient", "category", "nod"} & set(item)


def test_buddy_request_accepts_nod_fields():
    c = api()
    rid = c.post("/buddy/request", json={"tool": "Send email", "category": "send", "nod": True,
                                         "recipient": "customer@example.com"}, headers=H).json()["id"]
    item = c.get("/buddy/summary", headers=H).json()["items"][0]
    assert item["id"] == rid and item["category"] == "send" and item["nod"] is True


def test_nod_timeout_fails_closed_and_is_logged(monkeypatch):
    c = api()
    r = _nod(c)
    real = buddy_mod.time.monotonic
    monkeypatch.setattr(buddy_mod.time, "monotonic", lambda: real() + buddy_mod.TIMEOUT_S + 1)
    assert c.get(f"/buddy/state?id={r['id']}", headers=H).json()["decision"] == "cancel"
    assert c.post("/buddy/decide", json={"id": r["id"], "decision": "allow"}, headers=H).status_code == 409
    assert c.get("/buddy/nods", headers=H).json()["nods"][0]["outcome"] == "expired"


def test_nod_log_outcomes_and_auth():
    c = api()
    assert c.get("/buddy/nods").status_code == 401
    a, b, d = _nod(c, title="Pay A"), _nod(c, title="Pay B", amount="£5"), _nod(c, title="Pay C")
    pending = _nod(c, title="Pay D")
    c.post("/buddy/decide", json={"id": a["id"], "decision": "allow"}, headers=H)
    c.post("/buddy/decide", json={"id": b["id"], "decision": "deny"}, headers=H)
    c.post("/buddy/decide", json={"id": d["id"], "decision": "cancel"}, headers=H)
    nods = c.get("/buddy/nods", headers=H).json()["nods"]
    assert [(n["title"], n["outcome"]) for n in nods] == [("Pay C", "stopped"), ("Pay B", "stopped"), ("Pay A", "approved")]
    assert pending["id"] not in [n["id"] for n in nods]   # pending is not an outcome yet
    assert nods[2]["amount"] == "£42.00" and nods[2]["category"] == "payment" and nods[2]["decided_at"] >= nods[2]["requested_at"]
    assert len(c.get("/buddy/nods?limit=1", headers=H).json()["nods"]) == 1
