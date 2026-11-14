import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def make_flow(tmp_path, **overrides):
    from mazhost import flow_routes

    settings = SimpleNamespace(flow_cloud=False, flow_cleanup_llm=False, groq_api_key="",
                               groq_key="", stt_provider="parakeet", flow_dir=str(tmp_path))
    for key, value in overrides.items():
        setattr(settings, key, value)
    fake = SimpleNamespace(s=settings, dir=Path(tmp_path), words=["Piblo", "Cardputer"])
    return fake


def make_client(flow):
    from mazhost.flow_routes import build_flow_router

    app = FastAPI()
    app.include_router(build_flow_router(flow))
    return TestClient(app)


def test_settings_default_to_paste_and_auto(tmp_path):
    api = make_client(make_flow(tmp_path))
    body = api.get("/flow/settings").json()
    assert body["input_mode"] == "paste"
    assert body["cleanup"] == "auto"
    assert body["press_enter"] is False
    assert body["effective_cleanup"] == "rules"
    assert body["has_groq_key"] is False


def test_patch_settings_persists_and_applies_to_live_flow(tmp_path):
    flow = make_flow(tmp_path, groq_api_key="k")
    api = make_client(flow)
    body = api.patch("/flow/settings", json={"input_mode": "type", "cleanup": "groq",
                                             "press_enter": True}).json()
    assert body["input_mode"] == "type" and body["effective_cleanup"] == "groq"
    assert flow.s.flow_cloud is True and flow.s.flow_cleanup_llm is False
    stored = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert stored == {"input_mode": "type", "cleanup": "groq", "press_enter": True, "stt": "auto"}

    flow2 = make_flow(tmp_path, groq_api_key="k")
    api2 = make_client(flow2)
    assert flow2.s.flow_cloud is True  # re-applied on router build, no Core restart needed
    assert api2.get("/flow/settings").json()["input_mode"] == "type"


def test_groq_without_key_falls_back_to_rules(tmp_path):
    flow = make_flow(tmp_path)
    api = make_client(flow)
    assert api.patch("/flow/settings", json={"cleanup": "groq"}).json()["effective_cleanup"] == "rules"


def test_cleanup_rules_wins_over_local_flag(tmp_path):
    flow = make_flow(tmp_path, flow_cleanup_llm=True)
    api = make_client(flow)
    api.patch("/flow/settings", json={"cleanup": "rules"})
    assert flow.s.flow_cleanup_llm is False and flow.s.flow_cloud is False


def test_dictionary_add_dedupe_and_remove(tmp_path):
    flow = make_flow(tmp_path)
    api = make_client(flow)
    assert api.post("/flow/dictionary", json={"word": "Kubernetes"}).status_code == 200
    api.post("/flow/dictionary", json={"word": "kubernetes"})  # case-insensitive duplicate
    words = api.get("/flow/dictionary").json()["words"]
    assert [w for w in words if w.lower() == "kubernetes"] == ["Kubernetes"]  # first spelling wins
    assert api.delete(f"/flow/dictionary/{'kubernetes'}").status_code == 200
    assert "kubernetes" not in api.get("/flow/dictionary").json()["words"]
    on_disk = (tmp_path / "dictionary.txt").read_text(encoding="utf-8")
    assert "kubernetes" not in on_disk
    assert flow.words == api.get("/flow/dictionary").json()["words"]


@pytest.mark.parametrize("word", ["", "   ", "a" * 65, "bad/word", "semi;colon", "quote\"d"])
def test_dictionary_rejects_bad_words(tmp_path, word):
    api = make_client(make_flow(tmp_path))
    assert api.post("/flow/dictionary", json={"word": word}).status_code in (400, 422)


def test_status_summarises_latency_and_errors(tmp_path):
    flow = make_flow(tmp_path)
    Path(tmp_path, "latency.log").write_text(
        "2026-11-14T10:00:00 dictate intent=paste stt=120 clean=3 total=130 via=rules stt_via=parakeet chars=42\n"
        "2026-11-14T10:01:00 dictate intent=note stt=200 clean=4 total=210 via=groq stt_via=parakeet chars=10\n"
        "garbage line without metrics\n",
        encoding="utf-8",
    )
    Path(tmp_path, "errors.log").write_text("2026-11-14T10:02:00 dictate failed ENOENT wav\n", encoding="utf-8")
    body = make_client(flow).get("/flow/status").json()
    assert body["count"] == 2
    assert body["recent"][0]["intent"] == "note" and body["recent"][0]["total_ms"] == 210
    assert body["avg_total_ms"] == 170
    assert body["p95_total_ms"] == 210
    assert body["errors"] and "ENOENT" in body["errors"][-1]


def test_status_on_empty_dir_is_safe(tmp_path):
    body = make_client(make_flow(tmp_path)).get("/flow/status").json()
    assert body == {"recent": [], "count": 0, "avg_total_ms": 0, "p95_total_ms": 0,
                    "errors": [], "effective_cleanup": "rules"}


def test_insert_text_uses_configured_mode(tmp_path, monkeypatch):
    from mazhost import flow, flow_routes

    flow_ = make_flow(tmp_path)
    calls = {}
    monkeypatch.setattr(flow_routes, "type_text", lambda text: calls.setdefault("typed", text))
    monkeypatch.setattr(flow, "paste", lambda text, enter=False: calls.setdefault("pasted", (text, enter)))
    assert flow_routes.insert_text("hello", False, flow_) == "paste"
    assert calls["pasted"] == ("hello", False)

    write_settings = flow_routes.write_settings
    write_settings(flow_, {"input_mode": "type", **{k: v for k, v in flow_routes.DEFAULTS.items() if k != "input_mode"}})
    assert flow_routes.insert_text("hello", True, flow_) == "type"
    assert calls["typed"] == "hello"