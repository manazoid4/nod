"""Local daily Markdown notes, with calendar recall and shared-topic wikilinks."""
from __future__ import annotations

import json
import os
import re
import tempfile
import threading
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

_STOP = set("a an and are as at be been bring but by can could did do for from had has have how i "
            "in is it its like me my of on or our please remember said say she so that the their them "
            "then there these they this to told us was we were what when where which who will with "
            "would you your about today yesterday last week monday tuesday wednesday thursday friday "
            "saturday sunday".split())
_LINKS = "\n\n<!-- piblo-related -->\n"
_LINKS_END = "<!-- /piblo-related -->"
_LOCK = threading.RLock()


def _topics(text: str) -> set[str]:
    return {word for word in re.findall(r"[^\W_]+", text.casefold()) if len(word) > 2 and word not in _STOP}


class MemoryNotes:
    def __init__(self, data_dir: str | Path, today: Callable[[], date] = date.today):
        self.dir = Path(data_dir) / "memory"
        self.today = today

    def resolve_relative(self, text: str) -> tuple[date, date] | None:
        today = self.today()
        if re.search(r"\byesterday\b", text, re.I):
            day = today - timedelta(days=1)
            return day, day
        if re.search(r"\blast week\b", text, re.I):
            monday = today - timedelta(days=today.weekday() + 7)
            return monday, monday + timedelta(days=6)
        if re.search(r"\btoday\b", text, re.I):
            return today, today
        for index, name in enumerate(("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")):
            if re.search(rf"\b(?:on|last) {name}\b", text, re.I):
                age = (today.weekday() - index) % 7
                if age == 0 and re.search(rf"\blast {name}\b", text, re.I):
                    age = 7
                day = today - timedelta(days=age)
                return day, day
        return None

    def _paths(self) -> list[Path]:
        return sorted(p for p in self.dir.glob("*.md") if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem))

    def _read(self, path: Path) -> dict:
        raw = path.read_text("utf-8")
        header = re.match(r"\A---\n(.*?)\n---\n", raw, flags=re.S)
        body = re.sub(r"\A---\n.*?\n---\n", "", raw, count=1, flags=re.S)
        related = re.search(re.escape(_LINKS) + r"(.*?)" + re.escape(_LINKS_END), body, re.S)
        text = body[:related.start()] + body[related.end():] if related else body
        tag_line = re.search(r"(?m)^tags:\s*(.+)$", header[1]) if header else None
        return {"date": path.stem, "text": text.strip(),
                "tags": sorted(_topics(text) | (_topics(tag_line[1]) if tag_line else set())),
                "links": re.findall(r"\[\[(\d{4}-\d{2}-\d{2})\]\]", related[1] if related else "")}

    def _write(self, path: Path, note: dict) -> None:
        old = path.read_text("utf-8") if path.exists() else ""
        matched = re.match(r"\A---\n(.*?)\n---\n", old, flags=re.S)
        header = matched[1] if matched else ""
        for key, value in (("date", path.stem), ("tags", json.dumps(note["tags"], ensure_ascii=False))):
            if re.search(rf"(?m)^{key}:.*$", header):
                header = re.sub(rf"(?m)^{key}:.*$", lambda _: f"{key}: {value}", header)
            else:
                header = (header + f"\n{key}: {value}").strip()
        content = f"---\n{header}\n---\n\n{note['text']}\n"
        if note["links"]:
            content = content.rstrip() + _LINKS + "Related: " + " ".join(f"[[{day}]]" for day in sorted(set(note["links"]))) + "\n" + _LINKS_END + "\n"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=self.dir,
                                             prefix=".memory-", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def remember(self, text: str) -> Path:
        text = text.strip()
        if not text or len(text) > 4000:
            raise ValueError("Memory must contain 1 to 4000 characters")
        with _LOCK:
            self.dir.mkdir(parents=True, exist_ok=True)
            path = self.dir / f"{self.today().isoformat()}.md"
            note = self._read(path) if path.exists() else {"text": "", "tags": [], "links": []}
            note["text"] = (note["text"] + "\n\n- " + text).strip()
            note["tags"] = sorted(set(note["tags"]) | _topics(note["text"]))
            for other_path in self._paths():
                if other_path == path:
                    continue
                try:
                    other = self._read(other_path)
                except UnicodeError:
                    continue
                if set(note["tags"]) & set(other["tags"]):
                    note["links"].append(other_path.stem)
                    if path.stem not in other["links"]:
                        other["links"].append(path.stem)
                        self._write(other_path, other)
            self._write(path, note)
            return path

    def recall(self, query: str, days: int = 7) -> list[dict]:
        if days < 1:
            raise ValueError("days must be positive")
        start, end = self.resolve_relative(query) or (self.today() - timedelta(days=days - 1), self.today())
        topics = _topics(query)
        with _LOCK:
            hits = []
            for path in reversed(self._paths()):
                if start.isoformat() <= path.stem <= end.isoformat():
                    try:
                        note = self._read(path)
                    except UnicodeError:
                        continue
                    if not topics or topics.intersection(note["tags"]):
                        hits.append(note)
            return sorted(hits, key=lambda note: (len(topics.intersection(note["tags"])), note["date"]), reverse=True)

    def context(self, query: str) -> str:
        """Select matching entries before capping context for spoken answers."""
        topics = _topics(query)
        excerpts = []
        for note in self.recall(query):
            lines = [line for line in note["text"].splitlines()
                     if not topics or topics.intersection(_topics(line))]
            if lines:
                excerpts.append(f"{note['date']}: {' '.join(lines)}")
        return "\n".join(excerpts)[:6000]


class MemoryInput(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


def build_memory_router(notes: MemoryNotes) -> APIRouter:
    """Mount inside Core's existing authenticated API."""
    router = APIRouter()

    @router.post("/memory")
    def remember(body: MemoryInput):
        try:
            path = notes.remember(body.text)
            return {"date": path.stem, "note": path.name}
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        except (OSError, UnicodeError) as error:
            raise HTTPException(503, "Could not save memory") from error

    @router.get("/memory/recall")
    def recall(q: str = Query("", max_length=4000), days: int = Query(7, ge=1, le=3660)):
        try:
            return {"notes": notes.recall(q, days)}
        except OSError as error:
            raise HTTPException(503, "Could not read memory") from error

    return router
