"""Agent approval queue: Claude Code hook -> Core -> device (Piblo)."""
from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from collections import deque
from datetime import date
from typing import Callable, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MAX_ITEMS = 50
MAX_EVENTS = 20     # notify-only ring buffer polled by the device
TIMEOUT_S = 60      # hook falls back to the terminal after this
WORKING_S = 90      # agent counts as 'working' this long after the last request
HALT_DEFAULT_MIN = 30
HALT_MAX_MIN = 480
HALT_REASON = "Halted from Piblo (permission request denied; running processes unaffected)"
MAX_AGENTS = 8
MAX_ALERTS = 50        # alert records kept (with their ack/snooze outcome)
SNOOZE_DEFAULT_MIN = 10
SNOOZE_MAX_MIN = 240
MAX_DELAY_S = 30 * 86400
AlertKind = Literal["reminder", "meeting", "deadline", "sla", "computer", "task_done", "approval", "info"]
Priority = Literal["low", "normal", "high", "urgent"]
AlertAction = Literal["ack", "snooze", "approve", "reject"]
OTHER = "other"
KIND_KEY = {"done": "done", "needs": "needs", "error": "errors", "usage": "usage"}

def _local_today() -> str:
    return date.today().isoformat()


class BuddyRequest(BaseModel):
    tool: str = Field(min_length=1, max_length=120)
    summary: str = Field(default="", max_length=200)
    session_id: str = Field(default="", max_length=120)
    project: str = Field(default="", max_length=60)


class BuddyDecision(BaseModel):
    id: str
    decision: Literal["allow", "deny", "allow_all", "cancel"]


class BuddyEvent(BaseModel):
    """Notify-only ping (done / usage / needs / error). It can never approve,
    deny or decide anything: it only ever lands in the event ring below."""
    kind: Literal["done", "usage", "needs", "error"]
    text: str = Field(default="", max_length=2000)
    source: str = Field(default="", max_length=40)


class AlertIn(BaseModel):
    """Generic notification (reminder, webhook, ...). kind=approval is routed into the
    existing approval queue, never into the notify ring."""
    source: str = Field(default="webhook", max_length=40)
    kind: AlertKind = "info"
    title: str = Field(min_length=1, max_length=60)
    body: str = Field(default="", max_length=200)
    priority: Priority = "normal"
    actions: list[AlertAction] = Field(default_factory=lambda: ["ack"], max_length=4)
    delay_seconds: int = Field(default=0, ge=0, le=MAX_DELAY_S)
    expires_in: int | None = Field(default=None, ge=1, le=MAX_DELAY_S)


class SnoozeBody(BaseModel):
    minutes: int = Field(default=SNOOZE_DEFAULT_MIN, ge=1, le=SNOOZE_MAX_MIN)


class AllowAll(BaseModel):
    session_id: str = Field(min_length=1, max_length=120)
    on: bool = False


class HaltBody(BaseModel):
    on: bool
    minutes: int | None = Field(default=None, ge=1, le=HALT_MAX_MIN)


class Buddy:
    def __init__(self, today: Callable[[], str] | None = None) -> None:
        self._today = today or _local_today
        self._day = self._today()
        self._counts: dict[str, int] = {}
        self._agents: dict[str, int] = {}
        self._last: dict | None = None
        self._cv = threading.Condition()
        self._items: dict[str, dict] = {}
        self._events: deque[dict] = deque(maxlen=MAX_EVENTS)  # separate from _items on purpose
        self._event_id = 0
        self._alerts: dict[str, dict] = {}   # id -> alert record incl. outcome
        self._halt_until_mono = 0.0
        self._halt_until_wall = 0.0
        # No persistent session-wide grants: every sensitive action needs a fresh decision.

    def _halted_locked(self) -> bool:
        if self._halt_until_mono and time.monotonic() >= self._halt_until_mono:
            self._halt_until_mono = self._halt_until_wall = 0.0
        return self._halt_until_mono > 0

    def halt_state(self) -> dict:
        with self._cv:
            return self._halt_state_locked()

    def _halt_state_locked(self) -> dict:
        halted = self._halted_locked()
        return {"ok": True, "halted": halted, "until":
                datetime.fromtimestamp(self._halt_until_wall, timezone.utc).isoformat()
                if halted else None}

    def set_halt(self, on: bool, minutes: int | None = None) -> dict:
        """Pause future nod-mediated asks; NEVER promises to stop running tools."""
        with self._cv:
            self._halted_locked()
            if on:
                duration = HALT_DEFAULT_MIN if minutes is None else minutes
                self._halt_until_mono = time.monotonic() + duration * 60
                self._halt_until_wall = time.time() + duration * 60
                self._roll()
                for item in self._items.values():
                    if item["decision"] in (None, "allow") and time.monotonic() < item["deadline"]:
                        if item["decision"] is None:
                            self._bump("denied")
                        item["decision"], item["reason"] = "deny", HALT_REASON
                self._cv.notify_all()
            else:
                self._halt_until_mono = self._halt_until_wall = 0.0
            return self._halt_state_locked()

    def _roll(self) -> None:
        current = self._today()
        if current != self._day:
            self._day, self._counts, self._agents, self._last = current, {}, {}, None

    def _bump(self, key: str) -> None:
        self._counts[key] = self._counts.get(key, 0) + 1

    def today(self) -> dict:
        with self._cv:
            self._roll()
            agents = sorted(self._agents.items(), key=lambda kv: (kv[0] == OTHER, -kv[1], kv[0]))
            return {"date": self._day, **{k: self._counts.get(k, 0)
                    for k in ("done", "needs", "errors", "usage", "approved", "denied")},
                    "agents": [{"source": src, "done": count} for src, count in agents],
                    "last": dict(self._last) if self._last else None}

    def post_event(self, kind: str, text: str, source: str = "") -> dict:
        with self._cv:
            self._roll()
            self._bump(KIND_KEY[kind])
            name = source.strip() or OTHER
            if kind == "done":
                named = sum(1 for a in self._agents if a != OTHER)
                if name not in self._agents and name != OTHER and named >= MAX_AGENTS:
                    name = OTHER
                self._agents[name] = self._agents.get(name, 0) + 1
            self._event_id += 1
            ev = {"id": self._event_id, "kind": kind, "text": text[:160],
                  "source": source, "ts": time.time()}
            self._events.append(ev)
            self._last = {key: ev[key] for key in ("kind", "text", "source", "ts")}
            return dict(ev)

    # ---- generic alerts (reminder / webhook / ...) ----
    def post_alert(self, a: AlertIn) -> dict:
        if a.kind == "approval":
            # Same queue, same authority/halt/timeout rules as the Claude Code hook.
            item = self.request(a.title, a.body, project=a.source[:60])
            return {"ok": True, "routed": "approval", "id": item["id"], "decision": item["decision"]}
        if any(x in ("approve", "reject") for x in a.actions):
            raise ValueError("approve_reject_only_for_approval_kind")
        now = time.time()
        with self._cv:
            aid = "al-" + uuid.uuid4().hex[:8]
            rec = {"id": aid, "source": a.source, "kind": a.kind, "title": a.title, "body": a.body,
                   "priority": a.priority, "actions": list(dict.fromkeys(a.actions)) or ["ack"],
                   "created_at": datetime.fromtimestamp(now, timezone.utc).isoformat(),
                   "due": now + a.delay_seconds, "fired": False, "outcome": None, "snooze_until": 0.0}
            if a.expires_in:
                rec["_exp"] = now + a.delay_seconds + a.expires_in
                rec["expires_at"] = datetime.fromtimestamp(rec["_exp"], timezone.utc).isoformat()
            self._alerts[aid] = rec
            while len(self._alerts) > MAX_ALERTS:
                self._alerts.pop(next(iter(self._alerts)))
            self._fire_due_locked()
            return {"ok": True, "routed": "alert", "id": aid, "scheduled": not rec["fired"]}

    def _fire_due_locked(self) -> None:
        """Lazy scheduler: due reminders and snoozes that ran out enter the ring when polled."""
        now = time.time()
        for rec in self._alerts.values():
            if rec["outcome"] == "acked" or now > rec.get("_exp", float("inf")):
                continue
            snoozed = rec["outcome"] == "snoozed"
            if snoozed and now < rec["snooze_until"]:
                continue
            if rec["fired"] and not snoozed:
                continue
            if not rec["fired"] and now < rec["due"]:
                continue
            rec["fired"], rec["outcome"] = True, None   # (re)fire: an expired snooze nags again
            self._event_id += 1
            public = {k: v for k, v in rec.items() if k not in ("due", "fired", "outcome", "snooze_until", "_exp", "outcome_at")}
            self._events.append({"id": self._event_id, "kind": "alert", "text": rec["title"],
                                 "source": rec["source"], "ts": now, "alert": public})

    def alert_outcome(self, aid: str, action: str, minutes: int = SNOOZE_DEFAULT_MIN) -> dict:
        with self._cv:
            rec = self._alerts.get(aid)
            if rec is None:
                raise KeyError(aid)
            if action not in rec["actions"]:
                raise ValueError("action_not_offered")
            rec["outcome"] = "acked" if action == "ack" else "snoozed"
            rec["outcome_at"] = time.time()
            if action == "snooze":
                rec["snooze_until"] = rec["outcome_at"] + minutes * 60
            return {"ok": True, "id": aid, "outcome": rec["outcome"]}

    def alerts(self) -> dict:
        with self._cv:
            self._fire_due_locked()
            return {"ok": True, "alerts": [{k: v for k, v in r.items() if k != "_exp"}
                                           for r in self._alerts.values()]}

    def events(self, since: int = 0) -> dict:
        with self._cv:
            self._fire_due_locked()
            return {"ok": True, "events": [dict(e) for e in self._events if e["id"] > since],
                    "last": self._event_id}

    def request(self, tool: str, summary: str, session_id: str = "", project: str = "") -> dict:
        with self._cv:
            rid = uuid.uuid4().hex[:8]
            auto = "deny" if self._halted_locked() else None
            if auto:
                self._roll()
                self._bump("denied")
            self._items[rid] = {"id": rid, "tool": tool, "summary": summary,
                                "session_id": session_id, "project": project, "t": time.time(),
                                "deadline": time.monotonic() + TIMEOUT_S,
                                "decision": auto}
            if auto:
                self._items[rid]["reason"] = HALT_REASON
            while len(self._items) > MAX_ITEMS:
                self._items.pop(next(iter(self._items)))  # dicts keep insertion order
            return dict(self._items[rid])

    def state(self, rid: str, wait: float = 0) -> dict:
        end = time.monotonic() + wait
        with self._cv:
            while True:
                item = self._items.get(rid)
                if item is None:
                    return {"id": rid, "decision": None, "known": False}
                if time.monotonic() >= item["deadline"]:
                    if not item["decision"]:
                        item["decision"] = "cancel"
                        self._cv.notify_all()
                    # A grant consumed after its deadline is never safe, even if
                    # somebody approved it while the hook was temporarily offline.
                    return {"id": rid, "decision": "cancel", "known": True, "expired": True}
                if item["decision"] or time.monotonic() >= end:
                    result = {"id": rid, "decision": item["decision"], "known": True}
                    if item.get("reason"):
                        result["reason"] = item["reason"]
                    return result
                self._cv.wait(end - time.monotonic())

    def pending(self) -> list[dict]:
        with self._cv:
            now = time.monotonic()
            return [dict(i) for i in self._items.values()
                    if not i["decision"] and now < i["deadline"]]

    def summary(self, limit: int = 3) -> dict:
        """Cheap device poll: oldest-first live pending items + idle/working/needs_you."""
        now = time.time()
        monotonic_now = time.monotonic()
        with self._cv:
            live = [i for i in self._items.values()
                    if not i["decision"] and monotonic_now < i["deadline"]]
            recent = any(now - i["t"] < WORKING_S for i in self._items.values())
            items = [{"id": i["id"], "tool": i["tool"], "summary": i["summary"],
                      "project": i.get("project", ""), "session_id": i["session_id"],
                      "left": max(0, int(i["deadline"] - monotonic_now))} for i in live[:limit]]
            return {"ok": True, "agent": "needs_you" if live else "working" if recent else "idle",
                    "count": len(live), "items": items}

    def decide(self, rid: str, decision: str) -> dict:
        with self._cv:
            item = self._items.get(rid)
            if item is None:
                raise KeyError(rid)
            if decision == "allow_all":
                raise ValueError("session_wide_approval_disabled")
            if time.monotonic() >= item["deadline"]:
                if not item["decision"]:
                    item["decision"] = "cancel"
                    self._cv.notify_all()
                raise TimeoutError("approval_expired")
            if item["decision"]:
                return dict(item)
            if decision not in ("allow", "deny", "cancel"):
                raise ValueError("unsupported_decision")
            if self._halted_locked() and decision == "allow":
                decision = "deny"
                item["reason"] = HALT_REASON
            item["decision"] = decision
            if decision != "cancel":
                self._roll()
                self._bump("approved" if decision == "allow" else "denied")
            self._cv.notify_all()
            return dict(item)

    def set_allow_all(self, session_id: str, on: bool) -> None:
        if on:
            raise ValueError("session_wide_approval_disabled")
        # Revocation stays backwards-compatible for old clients. Nothing to revoke.


def install_buddy_routes(api: FastAPI, buddy: Buddy | None = None) -> Buddy:
    buddy = buddy or Buddy()

    @api.post("/buddy/request")
    def buddy_request(body: BuddyRequest):
        return buddy.request(body.tool, body.summary, body.session_id, body.project)

    @api.get("/buddy/state")
    def buddy_state(id: str, wait: float = 0):
        return buddy.state(id, min(max(wait, 0), 30))

    @api.get("/buddy/summary")
    def buddy_summary():
        return buddy.summary()

    @api.get("/buddy/pending")
    def buddy_pending():
        return {"ok": True, "pending": buddy.pending()}

    @api.post("/buddy/decide")
    def buddy_decide(body: BuddyDecision):
        try:
            return buddy.decide(body.id, body.decision)
        except KeyError:
            raise HTTPException(404, "request_not_found")
        except TimeoutError:
            raise HTTPException(409, "approval_expired")
        except ValueError as error:
            raise HTTPException(400, str(error))

    @api.post("/buddy/allow-all")
    def buddy_allow_all(body: AllowAll):
        try:
            buddy.set_allow_all(body.session_id, body.on)
        except ValueError as error:
            raise HTTPException(400, str(error))
        return {"ok": True, "session_id": body.session_id, "on": False}

    @api.post("/buddy/event")
    def buddy_event(body: BuddyEvent):
        return {"ok": True, **buddy.post_event(body.kind, body.text, body.source)}

    @api.post("/buddy/alert")
    def buddy_alert(body: AlertIn):
        try:
            return buddy.post_alert(body)
        except ValueError as error:
            raise HTTPException(400, str(error))

    @api.get("/buddy/alerts")
    def buddy_alerts():
        return buddy.alerts()

    @api.post("/buddy/alert/{aid}/{action}")
    def buddy_alert_action(aid: str, action: Literal["ack", "snooze"], body: SnoozeBody | None = None):
        try:
            return buddy.alert_outcome(aid, action, (body or SnoozeBody()).minutes)
        except KeyError:
            raise HTTPException(404, "alert_not_found")
        except ValueError as error:
            raise HTTPException(400, str(error))

    @api.get("/buddy/today")
    def buddy_today():
        return {"ok": True, **buddy.today()}

    @api.get("/buddy/events")
    def buddy_events(since: int = 0):
        return buddy.events(since)

    @api.get("/buddy/halt")
    def buddy_halt_get():
        return buddy.halt_state()

    @api.post("/buddy/halt")
    def buddy_halt(body: HaltBody):
        return buddy.set_halt(body.on, body.minutes)

    return buddy
