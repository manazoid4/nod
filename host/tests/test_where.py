from datetime import datetime, timezone
import os

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from mazhost import dumps, library
from mazhost.buddy import AlertIn, Buddy
from mazhost.config import Settings
from mazhost.focus import Focus
from mazhost.where import build_where_router


def setup(tmp_path):
    cfg = Settings(dumps_dir=str(tmp_path / "dumps"), project_roots=str(tmp_path / "projects"), _env_file=None)
    buddy = Buddy()
    focus = Focus(log_file=str(tmp_path / "focus.jsonl"), clock=lambda: 1000)
    api = FastAPI()
    api.include_router(build_where_router(cfg, buddy, focus))
    return TestClient(api), cfg, buddy, focus


@pytest.mark.parametrize("text", ["Park: Finish the sketch", "Finish the sketch"])
def test_park_persists_and_heads_history(tmp_path, text):
    c, cfg, _, _ = setup(tmp_path)
    r = c.post("/park", json={"text": text})
    assert r.status_code == 200
    saved = r.json()
    assert saved["title"] == "Finish the sketch"
    assert c.get("/where").json()["items"][0]["id"] == saved["id"]
    note = dumps.list_dumps(cfg.dumps_dir)[0]
    assert dumps.get_dump(cfg.dumps_dir, note["id"])["transcript"] == "Finish the sketch"
    assert note["kind"] == "park"


def test_mixed_history_sorts_times_and_skips_hidden_documents(tmp_path, monkeypatch):
    c, cfg, buddy, focus = setup(tmp_path)
    root = tmp_path / "projects"
    root.mkdir()
    visible = root / "draft.md"
    visible.write_text("draft")
    os.utime(visible, (2000, 2000))
    for sub in (".hidden", "node_modules"):
        (root / sub).mkdir()
        (root / sub / "new.md").write_text("ignore")
    focus.start(task="Write the introduction")
    monkeypatch.setattr("mazhost.buddy.time.time", lambda: 3000)
    acked = buddy.post_alert(AlertIn(source="test", title="Finished reminder"))["id"]
    buddy.alert_outcome(acked, "ack")
    buddy.post_alert(AlertIn(source="test", title="Call dentist", delay_seconds=600))
    library.save_item(tmp_path / "dumps" / "library", text="Saved reference", saved="1970-01-01T01:06:40+00:00")
    # Library ingestion time is the save activity, even for an older imported reference.
    c.post("/park", json={"text": "Return to this"})
    items = c.get("/where").json()["items"]
    assert [i["kind"] for i in items] == ["park", "library", "alert", "document", "focus"]
    assert [datetime.fromisoformat(i["when"]).timestamp() for i in items] == sorted(
        [datetime.fromisoformat(i["when"]).timestamp() for i in items], reverse=True)
    assert all(i["send_to_phone"] is True and i["source"] for i in items)
    assert next(i for i in items if i["kind"] == "document")["title"] == "draft.md"
    assert "Finished reminder" not in str(items)


def test_phone_uses_alert_events_consumed_by_android_companion(tmp_path):
    c, _, buddy, _ = setup(tmp_path)
    item = c.post("/park", json={"text": "Check the sketch"}).json()
    r = c.post(f"/where/{item['id']}/phone")
    assert r.status_code == 200
    assert r.json()["routed"] == "alert"
    event = buddy.events()["events"][-1]
    assert event["kind"] == "alert"
    assert event["alert"]["title"] == "Check the sketch"
    assert not any(e["kind"] == "text_input" for e in buddy.events()["events"])
    assert c.post("/where/missing/phone").status_code == 404


def test_latest_park_wins_when_captures_share_a_timestamp(tmp_path, monkeypatch):
    from mazhost import dumps

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 11, 12, tzinfo=timezone.utc)

    monkeypatch.setattr(dumps, "datetime", FixedDatetime)
    c, _, _, _ = setup(tmp_path)
    first = c.post("/park", json={"text": "First thought"}).json()
    second = c.post("/park", json={"text": "Second thought"}).json()
    assert [i["id"] for i in c.get("/where").json()["items"]] == [second["id"], first["id"]]


@pytest.mark.parametrize("text", ["", "   ", "Park:", "x" * 50001])
def test_park_rejects_empty_or_oversized_text(tmp_path, text):
    c, _, _, _ = setup(tmp_path)
    assert c.post("/park", json={"text": text}).status_code == 422


def test_new_routes_require_bearer_auth(tmp_path):
    from mazhost.app import create_app
    cfg = Settings(token="breadth-test-auth", dumps_dir=str(tmp_path / "dumps"), data_dir=str(tmp_path / "data"), _env_file=None)
    c = TestClient(create_app(cfg))
    for method, path, body in [("get", "/where", None), ("post", "/park", {"text": "hello"}),
                               ("get", "/rescue", None), ("get", "/rescue/compact", None),
                               ("get", "/memory/recall?q=dentist", None)]:
        kwargs = {"json": body} if body is not None else {}
        assert getattr(c, method)(path, **kwargs).status_code == 401
    assert c.get("/where", headers={"Authorization": f"Bearer {cfg.token}"}).status_code == 200


def test_rescue_put_allowed_from_configured_browser_origin(tmp_path):
    from mazhost.app import create_app
    cfg = Settings(token="breadth-test-auth", data_dir=str(tmp_path), web_origins="https://piblo.example", _env_file=None)
    c = TestClient(create_app(cfg))
    response = c.options("/rescue", headers={"Origin": "https://piblo.example",
        "Access-Control-Request-Method": "PUT", "Access-Control-Request-Headers": "authorization,content-type"})
    assert response.status_code == 200
    assert "PUT" in response.headers["access-control-allow-methods"]
