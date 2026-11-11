"""Speaks first when it matters: "Leave now for <title>", "Meeting in 10",
"Deadline today: <x>". Nudges go through the existing buddy.post_alert path,
each only once (idempotency key), and Focus holds non-urgent nudges back.

No network calls in this pack: travel time comes from a TransportProvider, and
the default is a static fake. Hook a free public transport feed or calendar
travel data into TransportProvider.travel_minutes later.
"""
from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any, Callable, Iterable

from .buddy import AlertIn, Buddy


class TransportProvider:
    """Interface: minutes of travel to a place. Replace with a live feed later."""

    def travel_minutes(self, destination: str) -> int:
        raise NotImplementedError


class StaticTransport(TransportProvider):
    """Default fake: one fixed travel time wherever the owner is going."""

    def __init__(self, minutes: int = 20) -> None:
        self.minutes = minutes

    def travel_minutes(self, destination: str) -> int:
        return self.minutes


_WARN_MIN = re.compile(r"(\d{1,3})\s*minutes?")


class SpeaksFirst:
    def __init__(
        self,
        buddy: Buddy,
        focus: Any = None,
        transport: TransportProvider | None = None,
        learning: Any = None,
        clock: Callable[[], float] = time.time,
        buffer_minutes: int = 5,
        warn_minutes: int = 10,
    ) -> None:
        self.buddy = buddy
        self.focus = focus
        self.transport = transport or StaticTransport()
        self.learning = learning
        self.clock = clock
        self.buffer_minutes = buffer_minutes
        self.warn_minutes = warn_minutes
        self._seen: set[str] = set()     # idempotency keys queued or posted
        self._held: list[AlertIn] = []   # non-urgent nudges held back by Focus

    def _muted(self) -> bool:
        if self.focus is None:
            return False
        muted = getattr(self.focus, "muted", False)
        return bool(muted() if callable(muted) else muted)

    def _warn(self) -> int:
        """Learning note may override the default warning minutes (pack 2.2)."""
        if self.learning is not None:
            match = _WARN_MIN.search(self.learning.notes_for("speaks_first"))
            if match:
                return max(1, min(180, int(match.group(1))))
        return self.warn_minutes

    @staticmethod
    def _ts(value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()

    def _post(self, key: str, alert: AlertIn, urgent: bool, posted: list[str], held: list[str]) -> None:
        if key in self._seen:
            return  # each nudge fires only once
        self._seen.add(key)
        alert.idempotency_key = key
        if not urgent and self._muted():
            self._held.append(alert)
            held.append(alert.title)
            return
        self.buddy.post_alert(alert)
        posted.append(alert.title)

    def _flush_held(self, posted: list[str]) -> None:
        if self._muted() or not self._held:
            return
        due, self._held = self._held, []
        for alert in due:
            self.buddy.post_alert(alert)
            posted.append(alert.title)

    def check(
        self,
        events: Iterable[dict[str, Any]] = (),
        deadlines: Iterable[dict[str, Any]] = (),
        now: float | None = None,
    ) -> dict[str, Any]:
        now = self.clock() if now is None else now
        posted: list[str] = []
        held: list[str] = []
        self._flush_held(posted)
        warn = self._warn()
        today = datetime.fromtimestamp(now).date()

        for event in events:
            start = self._ts(event["start"])
            title = str(event.get("title") or "event")[:40]
            if now >= start:
                continue  # already started: leave-now and meeting-in-N would both be wrong
            location = str(event.get("location") or "").strip()
            if location:
                travel = self.transport.travel_minutes(location)
                leave_at = start - (travel + self.buffer_minutes) * 60
                if now >= leave_at:
                    self._post(f"sf:leave:{title}:{int(start)}", AlertIn(
                        source="speaks_first", kind="meeting", title=f"Leave now for {title}"[:60],
                        priority="urgent", actions=["ack"],
                    ), urgent=True, posted=posted, held=held)
            if now >= start - warn * 60:
                self._post(f"sf:meeting:{title}:{int(start)}", AlertIn(
                    source="speaks_first", kind="meeting", title=f"Meeting in {warn}: {title}"[:60],
                    priority="high", actions=["ack", "snooze"],
                ), urgent=False, posted=posted, held=held)

        for deadline in deadlines:
            title = str(deadline.get("title") or "deadline")[:40]
            due_day = datetime.fromtimestamp(self._ts(deadline["due"])).date()
            if due_day != today:
                continue
            self._post(f"sf:deadline:{title}:{due_day.isoformat()}", AlertIn(
                source="speaks_first", kind="deadline", title=f"Deadline today: {title}"[:60],
                priority="normal", actions=["ack"],
            ), urgent=False, posted=posted, held=held)

        return {"ok": True, "posted": posted, "held": held}
