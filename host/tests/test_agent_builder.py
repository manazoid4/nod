from __future__ import annotations

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from mazhost.agent_builder import AgentBuilder
from mazhost.app import create_app
from mazhost.config import Settings
from mazhost.skill_vault import SkillVault

TOKEN = "test-token-that-is-not-default"
H = {"Authorization": f"Bearer {TOKEN}"}


class Clock:
    def __init__(self, t: float) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


def at(day: str, hhmm: str) -> float:
    return datetime.fromisoformat(f"{day}T{hhmm}:00").timestamp()


def builder(tmp_path, clock=None, llm=None, buddy=None):
    cfg = Settings(
        _env_file=None, token=TOKEN,
        skill_vault_dir=str(tmp_path / "skills"),
        skill_draft_dir=str(tmp_path / "drafts"),
        teach_dir=str(tmp_path / "teach"),
    )
    return AgentBuilder(cfg, SkillVault(cfg, llm or object()), tmp_path / "data",
                        llm=llm, clock=clock or Clock(at("2026-11-11", "09:00")), buddy=buddy)


def test_email_example_builds_daily_0800_just_do_it(tmp_path):
    b = builder(tmp_path)
    agent = b.build_agent("Make me an agent that checks my email at 8 and tells me what matters")
    assert agent["schedule"] == {"kind": "daily", "time": "08:00"}
    assert agent["level"] == "just_do_it"  # it only reads and tells
    assert "email" in agent["name"].lower()
    # skill file follows skill_vault conventions: vault/<slug>/SKILL.md + provenance.json
    skill = (tmp_path / "skills" / agent["slug"] / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---") and "## Procedure" in skill
    prov = json.loads((tmp_path / "skills" / agent["slug"] / "provenance.json").read_text(encoding="utf-8"))
    assert prov["state"] == "approved" and prov["source"] == "agent_builder"
    # schedule entry persisted in a JSON file in the data dir
    saved = json.loads((tmp_path / "data" / "agents.json").read_text(encoding="utf-8"))
    assert saved["agents"][0]["id"] == agent["id"]


@pytest.mark.parametrize("text,level", [
    ("Send my partner a message when I leave work", "ask_on_piblo"),
    ("Book my train every weekday at 7", "ask_on_piblo"),
    ("Post my standup notes at 17:30", "ask_on_piblo"),
    ("Pay my bills", "never"),
    ("Delete my old photos every 6 hours", "never"),
    ("email my boss at 8", "ask_on_piblo"),
    ("check my email at 8 and tell me what matters", "just_do_it"),
    ("check my email at 8 and forward the urgent one", "ask_on_piblo"),
    ("check email while organising files", "ask_on_piblo"),
    ("read my calendar while coordinating the team", "ask_on_piblo"),
    ("check email by organising files", "ask_on_piblo"),
    ("read the calendar about coordinating the team", "ask_on_piblo"),
    ("Order lunch every weekday", "never"),
    ("Erase the old backups", "never"),
    ("paying rent", "never"),
    ("bought groceries", "never"),
    ("deleted my backups", "never"),
    ("erased my notes", "never"),
])
def test_level_defaults_from_verbs(tmp_path, text, level):
    assert builder(tmp_path).build_agent(text)["level"] == level


def test_llm_level_can_only_go_stricter(tmp_path):
    class SneakyLLM:
        def chat(self, messages, route):
            return json.dumps({
                "name": "Bill payer", "job": "Pay my bills automatically",
                "schedule": {"kind": "daily", "time": "09:00"},
                "level": "just_do_it",  # never allowed for payments
            }), "sneaky"

    agent = builder(tmp_path, llm=SneakyLLM()).build_agent("Pay my bills every morning")
    assert agent["level"] == "never"

    class GoodLLM:
        def chat(self, messages, route):
            return json.dumps({
                "name": "Inbox triage", "job": "Read my email and tell me what matters",
                "schedule": {"kind": "weekdays", "time": "08:30"},
                "level": "just_do_it",
            }), "good"

    agent = builder(tmp_path, llm=GoodLLM()).build_agent("check my email at 8 and tell me what matters")
    assert agent["schedule"] == {"kind": "weekdays", "time": "08:30"} and agent["level"] == "just_do_it"


def test_broken_llm_falls_back_to_rules(tmp_path):
    class BrokenLLM:
        def chat(self, messages, route):
            raise RuntimeError("no_provider")

    agent = builder(tmp_path, llm=BrokenLLM()).build_agent("check my email at 8 and tell me what matters")
    assert agent["schedule"]["time"] == "08:00" and agent["level"] == "just_do_it"


def test_due_agents_with_fake_clock(tmp_path):
    clock = Clock(at("2026-11-11", "07:59"))  # Wednesday
    b = builder(tmp_path, clock=clock)
    daily = b.build_agent("check my email at 8 and tell me what matters")
    later = b.build_agent("tidy my desk at 9")
    hourly = b.build_agent("check the weather every 2 hours")
    weekday = b.build_agent("check my calendar at 8 on weekdays")
    assert b.due_agents(clock.t) == []  # nothing due yet

    clock.t = at("2026-11-11", "08:00")
    assert {a["id"] for a in b.due_agents(clock.t)} == {daily["id"], weekday["id"]}

    # dispatch through an injected fake runner, never agent_runner.py in tests
    ran = []
    assert b.run_due(ran.append, clock.t) == [daily["id"], weekday["id"]]
    assert [a["id"] for a in ran] == [daily["id"], weekday["id"]]
    assert b.due_agents(clock.t) == []  # marked run: no re-fire at the same minute

    clock.t = at("2026-11-11", "09:00")
    assert [a["id"] for a in b.due_agents(clock.t)] == [later["id"]]
    clock.t = at("2026-11-11", "10:00")  # 2h1m since the interval agent was built at 07:59
    assert {a["id"] for a in b.due_agents(clock.t)} == {later["id"], hourly["id"]}

    clock.t = at("2026-11-14", "09:00")  # Saturday: weekdays agent rests
    assert {a["id"] for a in b.due_agents(clock.t)} == {daily["id"], later["id"], hourly["id"]}


def test_runner_requires_approval_and_never_agents_do_not_run(tmp_path):
    class DenyBuddy:
        def request(self, *args, **kwargs):
            return {"id": "pending"}

        def state(self, request_id, wait=0):
            return {"decision": "deny"}

    clock = Clock(at("2026-11-11", "08:00"))
    b = builder(tmp_path, clock=clock, buddy=DenyBuddy())
    safe = b.build_agent("check email at 8")
    approval = b.build_agent("email my boss at 8")
    locked = b.build_agent("delete old backups at 8")
    ran = []

    assert b.run_due(ran.append, clock.t) == [safe["id"]]
    assert [agent["id"] for agent in ran] == [safe["id"]]
    assert approval["id"] not in [agent["id"] for agent in ran]
    assert locked["id"] not in [agent["id"] for agent in ran]

    class AllowBuddy:
        def request(self, *args, **kwargs):
            return {"id": "approved", "decision": "allow"}

    allowed = builder(tmp_path / "allowed", clock=clock, buddy=AllowBuddy())
    action = allowed.build_agent("email my boss at 8")
    ran.clear()
    assert allowed.run_due(ran.append, clock.t) == [action["id"]]
    assert ran[0]["id"] == action["id"]


def test_lowering_level_requires_approved_piblo_request(tmp_path):
    class BuddyDecision:
        def __init__(self, decision):
            self.decision = decision
            self.requested = []

        def request(self, *args, **kwargs):
            self.requested.append((args, kwargs))
            return {"id": "request", "decision": self.decision}

    denied = BuddyDecision("deny")
    b = builder(tmp_path / "denied", buddy=denied)
    agent = b.build_agent("email my boss at 8")
    with pytest.raises(ValueError, match="level_requires_approval"):
        b.set_level(agent["id"], "just_do_it")
    assert b.list()[0]["level"] == "ask_on_piblo"
    assert denied.requested

    allowed = BuddyDecision("allow")
    b = builder(tmp_path / "allowed", buddy=allowed)
    agent = b.build_agent("email my boss at 8")
    assert b.set_level(agent["id"], "just_do_it")["level"] == "just_do_it"


def test_routes_behind_bearer_token(tmp_path, monkeypatch):
    monkeypatch.setenv("MAZ_SKILL_VAULT_DIR", str(tmp_path / "skills"))
    monkeypatch.setenv("MAZ_SKILL_DRAFT_DIR", str(tmp_path / "drafts"))
    monkeypatch.setenv("MAZ_TEACH_DIR", str(tmp_path / "teach"))
    c = TestClient(create_app(Settings(token=TOKEN, data_dir=str(tmp_path / "data"), _env_file=None)))
    assert c.get("/agents").status_code == 401

    r = c.post("/agents/build", json={"text": "check my email at 8 and tell me what matters"}, headers=H)
    assert r.status_code == 200, r.text
    agent = r.json()
    assert agent["schedule"]["time"] == "08:00" and agent["level"] == "just_do_it"
    assert [a["id"] for a in c.get("/agents", headers=H).json()["agents"]] == [agent["id"]]

    r = c.post(f"/agents/{agent['id']}/level", json={"level": "ask_on_piblo"}, headers=H)
    assert r.status_code == 200 and r.json()["level"] == "ask_on_piblo"
    assert c.post(f"/agents/{agent['id']}/level", json={"level": "yolo"}, headers=H).status_code == 400
    assert c.post("/agents/agt_bogus/level", json={"level": "never"}, headers=H).status_code == 404

    assert c.delete(f"/agents/{agent['id']}", headers=H).json() == {"ok": True, "id": agent["id"]}
    assert c.get("/agents", headers=H).json()["agents"] == []
    assert not (tmp_path / "skills" / agent["slug"]).exists()  # its skill folder went with it
    assert c.delete(f"/agents/{agent['id']}", headers=H).status_code == 404
