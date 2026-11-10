"""Phone keyboard mode: POST /buddy/text, GET /buddy/text/{id}, POST .../ack."""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from mazhost import buddy as buddy_mod
from mazhost.app import create_app
from mazhost.config import Settings

TOKEN = "test-token-that-is-not-default"
H = {"Authorization": f"Bearer {TOKEN}"}
PHONE = "android/1.2"


def api():
    return TestClient(create_app(Settings(token=TOKEN, _env_file=None)))


def uid():
    return str(uuid.uuid4())


def test_post_get_and_event_ring():
    c = api()
    cid = uid()
    r = c.post("/buddy/text", json={"id": cid, "text": "hello from phone", "mode": "insert"},
               headers={**H, "X-Piblo-Client": PHONE})
    assert r.status_code == 200
    rec = r.json()
    assert rec["status"] == "pending" and rec["text"] == "hello from phone" and rec["mode"] == "insert"
    assert rec["client"] == PHONE
    got = c.get(f"/buddy/text/{cid}", headers=H)
    assert got.status_code == 200 and got.json()["id"] == cid and got.json()["status"] == "pending"
    events = c.get("/buddy/events", headers=H).json()["events"]
    assert len(events) == 1
    ev = events[-1]
    assert ev["kind"] == "text_input" and ev["text"] == "hello from phone"
    assert ev["text_input"] == {"id": cid, "text": "hello from phone", "mode": "insert"}


def test_auth_required():
    c = api()
    cid = uid()
    body = {"id": cid, "text": "hi", "mode": "insert"}
    assert c.post("/buddy/text", json=body).status_code == 401
    assert c.post("/buddy/text", json=body, headers={"Authorization": "Bearer nope"}).status_code == 401
    assert c.get(f"/buddy/text/{cid}").status_code == 401
    assert c.post(f"/buddy/text/{cid}/ack", json={"status": "inserted"}).status_code == 401


def test_validation_is_400():
    c = api()
    good = {"id": uid(), "text": "hi", "mode": "insert"}
    for bad in (
        {},  # missing everything
        {**good, "id": "not-a-uuid"},
        {**good, "id": ""},
        {**good, "text": ""},
        {**good, "text": "x" * 501},
        {**good, "mode": "approve"},  # untrusted text is never a command
        {**good, "mode": ""},
    ):
        assert c.post("/buddy/text", json=bad, headers=H).status_code == 400, bad
    assert c.post("/buddy/text", content="not json", headers={**H, "Content-Type": "application/json"}).status_code == 400
    assert c.post("/buddy/text", json=["not", "a", "dict"], headers=H).status_code == 400
    # valid again after the failures; header absent is fine too
    assert c.post("/buddy/text", json=good, headers=H).status_code == 200


def test_dedupe_same_id_no_second_event():
    c = api()
    cid = uid()
    body = {"id": cid, "text": "once only", "mode": "insert"}
    first = c.post("/buddy/text", json=body, headers=H)
    second = c.post("/buddy/text", json=body, headers=H)
    assert first.status_code == second.status_code == 200
    assert first.json()["id"] == second.json()["id"] == cid
    events = c.get("/buddy/events", headers=H).json()["events"]
    assert [e["kind"] for e in events] == ["text_input"]  # exactly one ring entry
    # even a different payload on a repeat id returns the original record
    retry = c.post("/buddy/text", json={"id": cid, "text": "tampered", "mode": "send"}, headers=H)
    assert retry.json()["text"] == "once only" and retry.json()["mode"] == "insert"
    assert c.get("/buddy/events", headers=H).json()["last"] == 1


def test_ack_flow_and_first_ack_wins():
    c = api()
    cid = uid()
    c.post("/buddy/text", json={"id": cid, "text": "typed", "mode": "insert"}, headers=H)
    ack = c.post(f"/buddy/text/{cid}/ack", json={"status": "inserted"}, headers=H)
    assert ack.status_code == 200 and ack.json()["status"] == "inserted"
    assert c.get(f"/buddy/text/{cid}", headers=H).json()["status"] == "inserted"
    again = c.post(f"/buddy/text/{cid}/ack", json={"status": "no_field"}, headers=H)
    assert again.status_code == 200 and again.json()["status"] == "inserted"  # first ack wins
    assert c.post(f"/buddy/text/{cid}/ack", json={"status": "approved"}, headers=H).status_code == 400
    assert c.post(f"/buddy/text/{uid()}/ack", json={"status": "inserted"}, headers=H).status_code == 404
    assert c.get(f"/buddy/text/{uid()}", headers=H).status_code == 404


def test_pending_bound_429_and_dedupe_still_works():
    c = api()
    ids = []
    for _ in range(buddy_mod.MAX_TEXT_PENDING):
        cid = uid()
        assert c.post("/buddy/text", json={"id": cid, "text": "x", "mode": "insert"}, headers=H).status_code == 200
        ids.append(cid)
    assert c.post("/buddy/text", json={"id": uid(), "text": "x", "mode": "insert"}, headers=H).status_code == 429
    # a repeat of an existing id returns the original even when full
    assert c.post("/buddy/text", json={"id": ids[0], "text": "x", "mode": "insert"}, headers=H).status_code == 200


def test_pending_freed_by_ack_and_expiry(monkeypatch):
    c = api()
    for _ in range(buddy_mod.MAX_TEXT_PENDING):
        c.post("/buddy/text", json={"id": uid(), "text": "x", "mode": "insert"}, headers=H)
    cid = uid()
    # ack one to free a slot (acked records no longer count as pending)
    oldest = c.get("/buddy/events", headers=H).json()["events"][0]["text_input"]["id"]
    c.post(f"/buddy/text/{oldest}/ack", json={"status": "no_field"}, headers=H)
    c.post("/buddy/text", json={"id": cid, "text": "after ack", "mode": "replace"}, headers=H)
    assert c.get(f"/buddy/text/{cid}", headers=H).json()["status"] == "pending"
    # after the 2-minute TTL the queued record is gone (404, never inserted late)
    real = buddy_mod.time.time
    monkeypatch.setattr(buddy_mod.time, "time", lambda: real() + buddy_mod.TEXT_TTL_S + 1)
    assert c.get(f"/buddy/text/{cid}", headers=H).status_code == 404
    assert c.post(f"/buddy/text/{cid}/ack", json={"status": "inserted"}, headers=H).status_code == 404


def test_text_is_literal_never_a_command():
    c = api()
    rid = c.post("/buddy/request", json={"tool": "Bash", "session_id": "s"}, headers=H).json()["id"]
    for text in ("Y approve", "decision: allow", "approve " + rid, "<script>", "Y\nAPPROVE"):
        cid = uid()
        r = c.post("/buddy/text", json={"id": cid, "text": text, "mode": "insert"}, headers=H)
        assert r.status_code == 200 and r.json()["text"] == text  # verbatim
    assert c.get(f"/buddy/state?id={rid}", headers=H).json()["decision"] is None
    assert [p["id"] for p in c.get("/buddy/pending", headers=H).json()["pending"]] == [rid]
    assert c.get("/buddy/summary", headers=H).json()["count"] == 1


def test_full_text_roundtrips_untruncated():
    c = api()
    cid = uid()
    big = "x" * 500  # non-ASCII is rejected: see test_unsupported_characters_rejected_not_silently_dropped
    assert c.post("/buddy/text", json={"id": cid, "text": big, "mode": "insert"}, headers=H).status_code == 200
    ev = c.get("/buddy/events", headers=H).json()["events"][-1]
    assert ev["text"] == big and ev["text_input"]["text"] == big


def test_smart_punctuation_folds_to_ascii():
    c = api()
    cid = uid()
    r = c.post("/buddy/text", json={"id": cid, "text": "it’s “fine” — ok…", "mode": "insert"}, headers=H)
    assert r.status_code == 200 and r.json()["text"] == "it's \"fine\" - ok..."
    assert c.get("/buddy/events", headers=H).json()["events"][-1]["text_input"]["text"] == "it's \"fine\" - ok..."


def test_unsupported_characters_rejected_not_silently_dropped():
    c = api()
    for text in ("café", "hi \U0001F600", "你好", "مرحبا"):
        r = c.post("/buddy/text", json={"id": uid(), "text": text, "mode": "insert"}, headers=H)
        assert r.status_code == 400 and r.json()["detail"] == "unsupported_characters", text
    assert c.get("/buddy/events", headers=H).json()["events"] == []


def test_device_can_ack_unsupported():
    c = api()
    cid = uid()
    c.post("/buddy/text", json={"id": cid, "text": "hello", "mode": "insert"}, headers=H)
    assert c.post(f"/buddy/text/{cid}/ack", json={"status": "unsupported"}, headers=H).json()["status"] == "unsupported"
