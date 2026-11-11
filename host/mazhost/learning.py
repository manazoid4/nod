"""Learning loop (Hermes-style, ideas only, no dependency).

Record how the owner reacts per feature (shown / acted / skipped / corrected),
distil the reactions into a per-user Markdown note in the data dir, and let other
features read that note next time. The note is plain text and the owner can edit
it: anything under "Your edits" is kept verbatim across rewrites, so edits win.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

EVENT_KINDS = ("shown", "acted", "skipped", "corrected")
_MANAGED_START = "<!-- piblo:managed -->"
_MANAGED_END = "<!-- /piblo:managed -->"
_USER_HEADING = "## Your edits — Piblo never changes this part"
_WEEK_S = 7 * 86400

_RULES_PROMPT = (
    "These are Piblo events for one feature: what was shown, acted on, skipped and corrected. "
    'Return JSON only: {"rules": ["plain rule the owner would agree with", ...]}. '
    "Rules are short imperatives or preferences, e.g. \"skip delivery updates\". "
    "No markdown, no extra keys.\n\nEVENTS:\n"
)


class Learning:
    def __init__(self, data_dir: str | Path, llm: Any = None, clock: Callable[[], float] = time.time) -> None:
        self.root = Path(data_dir).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)
        self.events_file = self.root / "learning-events.jsonl"
        self.llm = llm
        self.clock = clock

    @staticmethod
    def _feature(feature: str) -> str:
        return re.sub(r"[^a-z0-9-]+", "-", feature.lower()).strip("-")[:40] or "general"

    def _note_path(self, feature: str) -> Path:
        return self.root / f"learning-{self._feature(feature)}.md"

    def record(self, feature: str, kind: str, text: str = "") -> dict[str, Any]:
        if kind not in EVENT_KINDS:
            raise ValueError("unknown_event_kind")
        row = {"ts": self.clock(), "feature": self._feature(feature), "kind": kind,
               "text": " ".join(text.split())[:200]}
        with self.events_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        return row

    def _events(self, feature: str | None = None) -> list[dict[str, Any]]:
        try:
            lines = self.events_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return []
        out = []
        for line in lines[-5000:]:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if feature is None or row.get("feature") == feature:
                out.append(row)
        return out

    def _llm_rules(self, events: list[dict[str, Any]]) -> list[str] | None:
        try:
            reply, _provider = self.llm.chat(
                [{"role": "system", "content": "You write per-user preference notes. JSON only."},
                 {"role": "user", "content": _RULES_PROMPT + json.dumps(events[-100:])}],
                "auto",
            )
            data = json.loads(reply)
            return [str(r).strip()[:160] for r in data["rules"] if str(r).strip()]
        except Exception:
            return None  # the brain is advisory: any failure falls back to simple counts

    def _count_rules(self, events: list[dict[str, Any]]) -> list[str]:
        shown: Counter[str] = Counter()
        skipped: Counter[str] = Counter()
        rules: list[str] = []
        for e in events:
            key = " ".join(e["text"].lower().split())
            if e["kind"] == "shown":
                shown[key] += 1
            elif e["kind"] == "skipped":
                skipped[key] += 1
        for key, n in skipped.items():
            # skipped 3+ times of 4 -> a skip rule
            if key and n >= 3 and n >= 3 * shown.get(key, 0):
                rules.append(f"Skip {key}")
        seen: set[str] = set()
        for e in events:
            key = " ".join(e["text"].lower().split())
            if e["kind"] == "corrected" and key and key not in seen:
                seen.add(key)
                rules.append(e["text"])
        return rules

    def rewrite_note(self, feature: str) -> dict[str, Any]:
        feature = self._feature(feature)
        events = self._events(feature)
        rules = self._llm_rules(events) if self.llm else None
        if rules is None:
            rules = self._count_rules(events)
        user = self._user_part(self._note_path(feature))
        body = [f"# {feature.replace('-', ' ').title()} — what Piblo has learned", "", _MANAGED_START]
        body += [f"- {r}" for r in rules] or ["- Nothing yet"]
        body += [_MANAGED_END, "", _USER_HEADING, ""]
        if user:
            body += [user, ""]
        text = "\n".join(body).rstrip() + "\n"
        path = self._note_path(feature)
        path.write_text(text, encoding="utf-8")
        return {"ok": True, "feature": feature, "rules": rules, "path": str(path)}

    @staticmethod
    def _user_part(path: Path) -> str:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return ""
        if _MANAGED_END in text:
            part = text.split(_MANAGED_END, 1)[1].strip()
            if part.startswith(_USER_HEADING):
                part = part[len(_USER_HEADING):].strip()
            return part
        return text.strip()  # a note written entirely by the user is all user content

    def notes_for(self, feature: str) -> str:
        """What other features read next time."""
        try:
            return self._note_path(feature).read_text(encoding="utf-8")
        except OSError:
            return ""

    def weekly_summary(self, now: float | None = None) -> str:
        """"Here's what I learned this week" in plain words. Editable, because it
        is just the notes."""
        now = self.clock() if now is None else now
        cutoff = now - _WEEK_S
        features = sorted({e["feature"] for e in self._events() if e["ts"] >= cutoff})
        lines: list[str] = []
        for feature in features:
            rules = [ln[2:].strip() for l in self.notes_for(feature).splitlines()
                     if (ln := l.strip()).startswith("- ") and ln[2:].strip() != "Nothing yet"]
            lines += [f"{feature.replace('-', ' ').title()}: {r}" for r in rules]
        if not lines:
            return "Here's what I learned this week: nothing new yet."
        return "Here's what I learned this week:\n" + "\n".join(f"- {ln}" for ln in lines)
