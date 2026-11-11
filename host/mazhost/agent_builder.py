"""Agent builder: "make me an agent that checks my email at 8 and tells me what
matters" becomes a saved agent — a skill note in the skill vault (same Markdown
layout as skill_vault.py) plus a schedule entry in a JSON file in the data dir.

Safety levels per agent, from docs/PRODUCT-SPEC.md:
  just_do_it   read, summarise, remind
  ask_on_piblo send, book, post (a key press on Piblo approves, via buddy.request)
  never        payments, deletions, unless the owner unlocks them
The level defaults from the verbs in the request and can only ever go stricter
than the verbs allow, never looser.
"""
from __future__ import annotations

import json
import re
import secrets
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import Settings
from .skill_vault import SkillVault, _slug

LEVELS = ("just_do_it", "ask_on_piblo", "never")
_SEVERITY = {level: i for i, level in enumerate(LEVELS)}

_NEVER_VERBS = re.compile(
    r"\b(pay|pays|paid|payment|payments?|bills?|invoices?|purchases?|buy|buys|buying"
    r"|transfers?|deletes?|deleting|deletion|destroy|wipe)\b", re.I)
_ASK_VERBS = re.compile(
    r"\b(sends?|sending|books?|booking|posts?|posting|messages?|messaging"
    r"|shares?|sharing|publish|reply|replies|respond|dm|texts?|texting)\b", re.I)

_AT_TIME = re.compile(r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*([ap])?m?\b", re.I)
_INTERVAL = re.compile(r"\bevery\s+(\d{1,3})\s*h(?:ou)?rs?\b", re.I)
_WEEKDAYS = re.compile(r"\b(week-?days?|every\s+weekday)\b", re.I)
_FILLER = re.compile(
    r"^\s*(?:please\s+)?(?:make|build|create|set\s*up|get)\s+(?:me\s+)?an?\s+agent\s+(?:that|to|for)\s+",
    re.I)

_SAFETY = {
    "just_do_it": "Read, summarise and remind only. Sending, booking, posting, paying or deleting is out of scope for this agent.",
    "ask_on_piblo": "Sending, booking or posting needs the owner's key press on Piblo first (the existing buddy.request approval path).",
    "never": "Payments and deletions stay locked unless the owner unlocks them on Piblo.",
}
_SCHEDULE_WORDS = {"daily": "every day", "weekdays": "on weekdays", "interval": "every few hours"}


def _level_for(text: str) -> str:
    """Strictest level the verbs demand. Nothing that sends, books, posts, pays
    or deletes may ever default to just_do_it."""
    if _NEVER_VERBS.search(text):
        return "never"
    if _ASK_VERBS.search(text):
        return "ask_on_piblo"
    return "just_do_it"


def _strictest(a: str, b: str) -> str:
    return a if _SEVERITY[a] >= _SEVERITY[b] else b


def _schedule_for(text: str) -> dict[str, Any]:
    low = text.lower()
    interval = _INTERVAL.search(low)
    if interval:
        return {"kind": "interval", "every_hours": max(1, min(168, int(interval.group(1))))}
    hh, mm = 9, 0
    at = _AT_TIME.search(low)
    if at:
        hh, mm = int(at.group(1)), int(at.group(2) or 0)
        if at.group(3) == "p" and hh < 12:
            hh += 12
        if at.group(3) == "a" and hh == 12:
            hh = 0
        if hh > 23:
            raise ValueError("invalid_time")
        mm = min(mm, 59)
    return {"kind": "weekdays" if _WEEKDAYS.search(low) else "daily", "time": f"{hh:02d}:{mm:02d}"}


def _job_for(text: str) -> str:
    job = _FILLER.sub("", text.strip())
    job = _AT_TIME.sub(" ", job)        # timing lives in the schedule, not the job
    job = _INTERVAL.sub(" ", job)
    job = _WEEKDAYS.sub(" ", job)
    job = " ".join(job.split()).strip(" ,.")
    return job[:200] or "Help with a recurring task"


def _name_for(job: str) -> str:
    name = job if len(job) <= 50 else job[:50].rsplit(" ", 1)[0]
    return (name[:1].upper() + name[1:])[:60]


_BUILD_PROMPT = (
    "Turn this Piblo agent request into JSON only with keys: "
    "name (short title), job (what the agent does, one sentence), "
    'schedule ({"kind": "daily"|"weekdays"|"interval", "time": "HH:MM" 24h, "every_hours": N}), '
    'level ("just_do_it" read/summarise/remind, "ask_on_piblo" send/book/post, "never" pay/delete). '
    "No markdown, no extra keys.\n\nREQUEST:\n"
)


class AgentBuilder:
    def __init__(
        self,
        settings: Settings,
        vault: SkillVault,
        data_dir: str | Path,
        llm: Any = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.vault = vault
        self.store_file = Path(data_dir).expanduser() / "agents.json"
        self.store_file.parent.mkdir(parents=True, exist_ok=True)
        self.llm = llm
        self.clock = clock
        self._agents: dict[str, dict[str, Any]] = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        try:
            data = json.loads(self.store_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return {a["id"]: a for a in data.get("agents", []) if a.get("id")}

    def _save(self) -> None:
        self.store_file.write_text(
            json.dumps({"agents": list(self._agents.values())}, indent=2), encoding="utf-8")

    def _llm_parse(self, text: str, llm: Any) -> tuple[str, str, dict[str, Any], str, str]:
        reply, provider = llm.chat(
            [{"role": "system", "content": "You configure Piblo agents. JSON only."},
             {"role": "user", "content": _BUILD_PROMPT + text[:1000]}],
            "auto",
        )
        data = json.loads(reply)
        if not isinstance(data, dict):
            raise ValueError("not_object")
        name = str(data["name"]).strip()[:60]
        job = str(data["job"]).strip()[:200]
        sched = data["schedule"]
        kind = sched.get("kind")
        if kind == "interval":
            schedule: dict[str, Any] = {"kind": "interval",
                                        "every_hours": max(1, min(168, int(sched["every_hours"])))}
        elif kind in ("daily", "weekdays"):
            hhmm = str(sched["time"])
            if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", hhmm):
                raise ValueError("invalid_time")
            schedule = {"kind": kind, "time": hhmm}
        else:
            raise ValueError("invalid_schedule")
        level = str(data.get("level") or "")
        if level not in LEVELS:
            level = "just_do_it"
        if not name or not job:
            raise ValueError("missing_name_or_job")
        # The verbs in the request set the floor; the LLM may only go stricter.
        level = _strictest(level, _level_for(f"{text} {job}"))
        return name, job, schedule, level, provider

    def build_agent(self, text: str, llm: Any = None) -> dict[str, Any]:
        text = " ".join(text.split()).strip()
        if len(text) < 3:
            raise ValueError("request_too_short")
        parsed: tuple[str, str, dict[str, Any], str, str] | None = None
        use_llm = llm or self.llm
        if use_llm:
            try:
                parsed = self._llm_parse(text, use_llm)
            except Exception:
                parsed = None  # the brain is advisory: any failure falls back to rules
        if parsed:
            name, job, schedule, level, provider = parsed
        else:
            job = _job_for(text)
            name = _name_for(job)
            schedule = _schedule_for(text)
            level = _level_for(f"{text} {job}")
            provider = "rule-based"

        agent_id = "agt_" + secrets.token_urlsafe(8)
        slug = _slug(name)
        n = 2
        while (self.vault.vault / slug).exists():
            slug, n = f"{_slug(name)}-{n}", n + 1
        root = self.vault.vault / slug
        root.mkdir(parents=True)
        skill_md = SkillVault._render_skill(name, {
            "description": job,
            "when_to_use": [f"Runs {_SCHEDULE_WORDS[schedule['kind']]} for the owner."],
            "procedure": [job, "Summarise the outcome in one plain sentence for the owner."],
            "verification": ["The owner can see what was done and why."],
            "safety": [_SAFETY[level]],
        })
        (root / "SKILL.md").write_text(skill_md, encoding="utf-8")
        (root / "provenance.json").write_text(json.dumps({
            "name": name, "slug": slug, "state": "approved", "provider": provider,
            "created_at": self.clock(), "source": "agent_builder", "agent_id": agent_id,
        }, indent=2), encoding="utf-8")

        agent = {
            "id": agent_id, "name": name, "slug": slug, "job": job,
            "schedule": schedule, "level": level, "skill_path": str(root),
            "created_at": self.clock(), "last_run_at": 0.0,
        }
        self._agents[agent_id] = agent
        self._save()
        return dict(agent)

    def list(self) -> list[dict[str, Any]]:
        return [dict(a) for a in
                sorted(self._agents.values(), key=lambda a: a["created_at"])]

    def _get(self, agent_id: str) -> dict[str, Any]:
        if not re.fullmatch(r"agt_[A-Za-z0-9_-]{6,40}", agent_id):
            raise KeyError(agent_id)
        agent = self._agents.get(agent_id)
        if agent is None:
            raise KeyError(agent_id)
        return agent

    def set_level(self, agent_id: str, level: str) -> dict[str, Any]:
        if level not in LEVELS:
            raise ValueError("unknown_level")
        agent = self._get(agent_id)
        agent["level"] = level
        self._save()
        return dict(agent)

    def delete(self, agent_id: str) -> dict[str, Any]:
        agent = self._get(agent_id)
        del self._agents[agent_id]
        self._save()
        # Only the folder this builder wrote for this agent.
        shutil.rmtree(Path(agent["skill_path"]), ignore_errors=True)
        return {"ok": True, "id": agent_id}

    def _due(self, agent: dict[str, Any], now: float) -> bool:
        sched = agent["schedule"]
        last = float(agent.get("last_run_at") or 0.0)
        if sched["kind"] == "interval":
            return now - max(last, float(agent["created_at"])) >= sched["every_hours"] * 3600
        hh, mm = (int(part) for part in sched["time"].split(":"))
        due_at = datetime.fromtimestamp(now).replace(hour=hh, minute=mm, second=0, microsecond=0).timestamp()
        if now < due_at or last >= due_at:
            return False
        if sched["kind"] == "weekdays" and datetime.fromtimestamp(now).weekday() >= 5:
            return False
        return True

    def due_agents(self, now: float | None = None) -> list[dict[str, Any]]:
        now = self.clock() if now is None else now
        return [dict(a) for a in self.list() if self._due(a, now)]

    def run_due(self, runner: Callable[[dict[str, Any]], Any], now: float | None = None) -> list[str]:
        """Dispatch due agents through agent_runner-style runner (a fake in tests).
        Marked run before dispatch so a failing runner cannot re-fire every tick."""
        now = self.clock() if now is None else now
        ran: list[str] = []
        for agent in self._agents.values():
            if not self._due(agent, now):
                continue
            agent["last_run_at"] = now
            self._save()
            runner(dict(agent))
            ran.append(agent["id"])
        return ran


class BuildRequest(BaseModel):
    text: str = Field(min_length=3, max_length=500)


class LevelRequest(BaseModel):
    level: str = Field(min_length=3, max_length=20)


def build_agent_router(builder: AgentBuilder) -> APIRouter:
    router = APIRouter(prefix="/agents", tags=["agents"])

    @router.post("/build")
    def build(body: BuildRequest):
        try:
            return builder.build_agent(body.text)
        except ValueError as error:
            raise HTTPException(400, str(error)) from error

    @router.get("")
    def list_agents():
        return {"ok": True, "agents": builder.list()}

    @router.post("/{agent_id}/level")
    def set_level(agent_id: str, body: LevelRequest):
        try:
            return builder.set_level(agent_id, body.level)
        except KeyError:
            raise HTTPException(404, "agent_not_found") from None
        except ValueError as error:
            raise HTTPException(400, str(error)) from error

    @router.delete("/{agent_id}")
    def delete_agent(agent_id: str):
        try:
            return builder.delete(agent_id)
        except KeyError:
            raise HTTPException(404, "agent_not_found") from None

    return router
